from datetime import datetime, timezone


def main():
    # Example 1: Interective start and end mission
    from vyomcloudbridge.utils.mission_utils import MissionUtils

    mission_utils = MissionUtils()
    new_mission_id = mission_utils.generate_mission_id()
    print("Trying to start mission_id with-", new_mission_id)
    try:
        try:
            mission_start_time = datetime.now(timezone.utc).isoformat()
            mission_detail, start_mission_error = mission_utils.start_mission(
                id=new_mission_id,
                start_time=mission_start_time,
                destination_ids=["s3"],
            )
            if start_mission_error:
                print(f"Error starting mission: {start_mission_error}")
                # take user input, to start the current mission (this will stop the existing mission)
                user_input = input("Try force starting the current mission? [Y/n]?")
                if user_input.lower() == "y":
                    force_start_mission_success, force_start_mission_error = (
                        mission_utils.start_mission(
                            start_time=mission_start_time,
                            destination_ids=["s3"],
                            force_start=True,
                        )
                    )
                    if force_start_mission_error:
                        raise Exception(force_start_mission_error)
                    else:
                        print("Mission started successfully.\n")
                else:
                    raise Exception(start_mission_error)
            else:
                print("Mission started successfully.")
        except Exception as e:
            raise

        # wait for the user input, "Shall we end current misssion? [Y/n]?"
        try:
            user_input = input("Shall we end current misssion? [Y/n]?")
            if user_input.lower() == "y":
                try:
                    success, error = mission_utils.end_current_mission(
                        destination_ids=["s3"]
                    )
                    if error:
                        print("Failed to end current mission:", error)
                    else:
                        print("Current mission ended successfully.")
                except KeyboardInterrupt:
                    print("MissionUtils service interrupted by user.")
                except Exception as e:
                    print(f"An error in ending current mission: {str(e)}")
                finally:
                    mission_utils.cleanup()
                    print("MissionUtils service cleaned up and exited.")
            else:
                print("Skipping marking mission as completed...")
        except KeyboardInterrupt:
            print("MissionUtils service interrupted by user.")
        except Exception as e:
            print(f"An error in ending current mission: {str(e)}")

        print("\n\n\nNow let's try to fetch the curremt mission status")
        current_mission_message, current_mission_error = (
            mission_utils.get_current_mission()
        )
        if current_mission_error:
            print(f"Error fetching current mission: {current_mission_error}")
        else:
            print(f"Current mission status: {current_mission_message}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    finally:
        mission_utils.cleanup()
        print("MissionUtils service cleaned up and exited.")


if __name__ == "__main__":
    main()
