"""WOFOST simulation worker thread."""

from datetime import date, timedelta
from typing import Dict

import pandas as pd
from PyQt5.QtCore import QThread, pyqtSignal

from config.crops import CROP_OPTIONS


class SimulationWorker(QThread):
    """Worker thread for running WOFOST simulations."""

    progress = pyqtSignal(int, str)
    finished = pyqtSignal(list, dict, object, int, str)
    error = pyqtSignal(str)

    def __init__(self, config: Dict):
        super().__init__()
        self.config = config

    def run(self):
        try:
            # Import PCSE modules
            self.progress.emit(5, "Importing PCSE modules...")
            from pcse.base import ParameterProvider
            from pcse.input import NASAPowerWeatherDataProvider, YAMLCropDataProvider
            from pcse.models import Wofost81_NWLP_CWB_CNB

            # Get configuration
            crop_name = self.config["crop"]
            crop_config = CROP_OPTIONS[crop_name]
            location = self.config["location"]
            soil_params = self.config["soil_params"]
            fert_scenarios = self.config["fert_scenarios"]
            start_date = self.config["start_date"]
            year = start_date.year

            # Load weather data
            self.progress.emit(15, f"Loading weather for {location['name']}...")
            weather = NASAPowerWeatherDataProvider(
                latitude=location["lat"], longitude=location["lon"]
            )

            # Store weather data for plotting
            year = start_date.year
            weather_data = []
            for d in pd.date_range(date(year, 1, 1), date(year, 12, 31)):
                try:
                    w = weather(d.date())
                    weather_data.append({
                        'date': d,
                        'tmax': w.TMAX,
                        'tmin': w.TMIN,
                        'rain': w.RAIN,
                        'radiation': w.IRRAD / 1000000,  # Convert J/m2 to MJ/m2
                    })
                except Exception as e:
                    print(e)
                    pass
            self.weather_df = pd.DataFrame(weather_data).set_index('date')
            self.weather_year = year
            self.location_name = location['name']

            results = []
            dataframes = {}
            total_scenarios = len(
                [s for s in fert_scenarios.values() if s.get("enabled", True)]
            )
            completed = 0

            for key, scenario in fert_scenarios.items():
                if not scenario.get("enabled", True):
                    continue

                progress_pct = 20 + int(70 * completed / total_scenarios)
                self.progress.emit(progress_pct, f"Running: {scenario['name']}...")

                # Build agromanagement
                planting_date = date(year, start_date.month, start_date.day)
                end_date = date(year, 12, 31)
                max_duration = crop_config["season_days"]

                # Build timed events for N applications
                timed_events = None
                if scenario["applications"]:
                    timed_events = []
                    for i, (days, amount, recovery) in enumerate(
                        scenario["applications"]
                    ):
                        app_date = planting_date + timedelta(days=days)
                        timed_events.append(
                            {
                                "event_signal": "apply_n",
                                "name": f"N application {i + 1}",
                                "comment": f"{amount} kg N/ha",
                                "events_table": [
                                    {
                                        app_date: {
                                            "N_amount": amount,
                                            "N_recovery": recovery,
                                        }
                                    }
                                ],
                            }
                        )

                agro = {
                    "Version": 1.0,
                    "AgroManagement": [
                        {
                            planting_date: {
                                "CropCalendar": {
                                    "crop_name": crop_name,
                                    "variety_name": crop_config["variety"],
                                    "crop_start_date": planting_date,
                                    "crop_start_type": "emergence",
                                    "crop_end_date": end_date,
                                    "crop_end_type": "earliest",
                                    "max_duration": max_duration,
                                },
                                "TimedEvents": timed_events,
                                "StateEvents": None,
                            }
                        }
                    ],
                }

                # Create crop data provider
                cropd = YAMLCropDataProvider(Wofost81_NWLP_CWB_CNB)
                cropd.set_active_crop(crop_name, crop_config["variety"])

                # Build soil data
                soildata = {
                    "SM0": soil_params["SM0"],
                    "SMFCF": soil_params["SMFCF"],
                    "SMW": soil_params["SMW"],
                    "CRAIRC": soil_params["CRAIRC"],
                    "RDMSOL": soil_params["RDMSOL"],
                    "K0": soil_params["K0"],
                    "SOPE": soil_params["SOPE"],
                    "KSUB": soil_params["KSUB"],
                    "IFUNRN": 0,
                    "SSMAX": 0.0,
                    "SSI": 0.0,
                    "WAV": 50.0,
                    "NOTINF": 0.0,
                    "SMLIM": soil_params["SMFCF"],
                    "NSOILBASE": soil_params["NSOILBASE"],
                    "NSOILBASE_FR": soil_params.get("NSOILBASE_FR", 0.025),
                }

                sitedata = {
                    "CO2": 415.0,
                    "NAVAILI": 20.0,
                    "BG_N_SUPPLY": 0.5,
                }

                # Create parameters
                params = ParameterProvider(
                    cropdata=cropd, soildata=soildata, sitedata=sitedata
                )

                # Apply vernalization override if needed
                if crop_config.get("needs_vern_override"):
                    params.set_override("VERNSAT", 0)
                    params.set_override("VERNBASE", 0)
                    params.set_override("VERNDVS", 0)

                try:
                    model = Wofost81_NWLP_CWB_CNB(params, weather, agro)
                    model.run_till_terminate()

                    output = model.get_output()
                    df = pd.DataFrame(output)
                    summary = model.get_summary_output()

                    if summary and len(summary) > 0:
                        s = summary[0]
                        grain_yield = s.get("TWSO", 0)

                        if crop_name in ["potato", "cassava", "sweetpotato"]:
                            main_yield = (
                                grain_yield
                                if grain_yield > 0
                                else s.get("TAGP", 0) * 0.5
                            )
                        else:
                            main_yield = (
                                grain_yield
                                if grain_yield > 0
                                else s.get("TAGP", 0) * 0.4
                            )

                            # Calculate GDD from weather data
                            gdd_list = []
                            daily_gdd_list = []
                            tbase = 0.0  # Base temperature
                            cumulative_gdd = 0.0
                            for d in df['day']:
                                try:
                                    # Convert to date object for weather provider
                                    if hasattr(d, 'date'):
                                        d_date = d.date()
                                    elif hasattr(d, 'timetuple'):
                                        d_date = d
                                    else:
                                        d_date = pd.Timestamp(d).date()

                                    wdata = weather(d_date)
                                    tmax = wdata.TMAX
                                    tmin = wdata.TMIN
                                    daily_gdd = max(0.0, (tmax + tmin) / 2.0 - tbase)
                                except Exception as e:
                                    print(e)
                                    daily_gdd = 0.0

                                cumulative_gdd += daily_gdd
                                daily_gdd_list.append(daily_gdd)
                                gdd_list.append(cumulative_gdd)

                            df['GDD'] = gdd_list
                            df['daily_GDD'] = daily_gdd_list

                            results.append({
                                'df': df,
                                'summary': s,
                                'yield_kg': main_yield,
                                'yield_t': main_yield / 1000,
                                'scenario': scenario['name'],
                                'scenario_key': key,
                                'n_rate': scenario['total_n'],
                                'tagp': s.get('TAGP', 0),
                                'laimax': s.get('LAIMAX', 0),
                            })

                        dataframes[scenario["name"]] = df

                except Exception as e:
                    print(f"Error in scenario {key}: {e}")

                completed += 1

            self.progress.emit(95, "Finalizing results...")
            self.progress.emit(100, "Done!")
            self.finished.emit(
                results, dataframes, self.weather_df, self.weather_year, self.location_name
            )

        except Exception as e:
            import traceback

            self.error.emit(f"Simulation error: {str(e)}\n{traceback.format_exc()}")
