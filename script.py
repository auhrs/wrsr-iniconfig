#!/usr/bin/env python3

import os
import sys
import time
import datetime
import shutil
import random
import re

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def exit_script():
    print("Exiting...")
    sys.exit(0)

def update_log(message):
    log_path = 'iniconfig.log'
    date_str = datetime.date.today().isoformat()
    time_str = time.strftime("%H:%M:%S")
    if os.path.exists(log_path):
        with open(log_path, 'r') as f:
            log_lines = f.readlines()
        if len(log_lines) >= 100:
            log_lines = log_lines[:-1]
    else:
        log_lines = ["[{date}], [{time}], iniconfig created logfile\n".format(
            date=date_str, time=time_str)]
    # Add new message on top
    log_lines = ["[{date}], [{time}], {message}\n".format(date=date_str, time=time_str, message=message)] + log_lines
    with open(log_path, 'w') as f:
        f.writelines(log_lines)

def main():
    try:
        while True:
            clear_screen()
            print("-" * 80)
            print("WRSR-INICONFIG | https://github.com/auhrs/wrsr-iniconfig/         (c) 2024 AUHRS")
            print("-" * 80)
            print("\nSELECT DIRECTORY TO MODIFY")
            print("wrsr-iniconfig modifies the ini files used by Workers and Resources: Soviet ")
            print("Republic. Please enter your working directory to continue.\n")
            print("Paste path to directory:")
            print("Or press ENTER for the current directory:")
            print("[{}]\n".format(os.getcwd()))
            print("Press CTRL+C to cancel all operations")
            print("-" * 80)
            working_directory = input().strip()
            if not working_directory:
                working_directory = os.getcwd()
            if not os.path.isdir(working_directory):
                print("Invalid directory. Press ENTER to try again.")
                input()
                continue

            while True:
                clear_screen()
                print("-" * 80)
                print("WRSR-INICONFIG | https://github.com/auhrs/wrsr-iniconfig/         (c) 2024 AUHRS")
                print("-" * 80)
                print("\nMENU")
                print("Your working directory:")
                print("[{}]\n".format(working_directory))
                print("\t1. Create free buildings")
                print("\t2. Restore all backups\n")
                print("Press CTRL+C to cancel all operations")
                print("-" * 80)
                choice = input("Enter your choice: ").strip()
                if choice == '1':
                    create_free_buildings(working_directory)
                    break
                elif choice == '2':
                    restore_backups(working_directory)
                    break
                else:
                    print("Invalid choice. Press ENTER to try again.")
                    input()
    except KeyboardInterrupt:
        exit_script()

def create_free_buildings(working_directory):
    while True:
        clear_screen()
        print("-" * 80)
        print("WRSR-INICONFIG | https://github.com/auhrs/wrsr-iniconfig/         (c) 2024 AUHRS")
        print("-" * 80)
        print("\nCREATE FREE BUILDINGS")
        print("Your working directory:")
        print("[{}]\n".format(working_directory))
        print("Do you want to modify building.ini files only, or do you want to rename each ")
        print("asset as well?\n")
        print("\t1. Modify building.ini only")
        print("\t2. Rename each asset according to building type")
        print("\t3. Let me rename each asset individually\n")
        print("Press CTRL+C to cancel all operations")
        print("-" * 80)
        sub_choice = input("Enter your choice: ").strip()
        if sub_choice == '1':
            modify_building_ini_only(working_directory)
            break
        elif sub_choice == '2':
            rename_assets_by_type(working_directory)
            break
        elif sub_choice == '3':
            rename_assets_individually(working_directory)
            break
        else:
            print("Invalid choice. Press ENTER to try again.")
            input()

def modify_building_ini_only(working_directory):
    failed_dirs = []
    success_dirs = []
    log_message = "iniconfig check: Modify building.ini only"
    update_log(log_message)
    for root, dirs, files in os.walk(working_directory):
        if 'building.ini' in files:
            try:
                building_ini_path = os.path.join(root, 'building.ini')
                backup_name = 'building.{date}.bak'.format(date=datetime.date.today().strftime("%Y%m%d"))
                backup_path = os.path.join(root, backup_name)
                shutil.copy2(building_ini_path, backup_path)
                with open(building_ini_path, 'r') as f:
                    lines = f.readlines()
                # Remove lines starting with the specified keys
                lines = [line for line in lines if not line.startswith((
                    '$COST_WORK', '$COST_RESOURCE', '$NO_LIFESPAN', '$HEATING_DISABLE',
                    '$WATERSEWAGE_DISABLE', '$WASTE_WORKERS_DISABLE', '$WASTE_CUSTOMERS_DISABLE',
                    '$COUNT_LIMIT', '$ELETRIC_WITHOUT_WORKING_FACTOR',
                    '$ELETRIC_WITHOUT_LIGHTING_FACTOR', '$NAME_STR', '$NAME'
                ))]
                # Find index to insert new lines after $NAME_STR or $NAME
                insert_index = None
                for i, line in enumerate(lines):
                    if line.startswith('$NAME_STR') or line.startswith('$NAME'):
                        insert_index = i + 1
                        break
                if insert_index is None:
                    insert_index = 0
                new_lines = lines[:insert_index] + [
                    '$NO_LIFESPAN\n',
                    '$HEATING_DISABLE\n',
                    '$WATERSEWAGE_DISABLE\n',
                    '$WASTE_WORKERS_DISABLE\n',
                    '$WASTE_CUSTOMERS_DISABLE\n',
                    '$COUNT_LIMIT 999\n',
                    '$ELETRIC_WITHOUT_WORKING_FACTOR 1\n',
                    '$ELETRIC_WITHOUT_LIGHTING_FACTOR 1\n'
                ] + lines[insert_index:]
                with open(building_ini_path, 'w') as f:
                    f.writelines(new_lines)
                success_dirs.append(os.path.relpath(root, working_directory))
            except Exception as e:
                failed_dirs.append((os.path.relpath(root, working_directory), str(e)))
    display_report(working_directory, success_dirs, failed_dirs)

def rename_assets_by_type(working_directory):
    clear_screen()
    print("-" * 80)
    print("WRSR-INICONFIG | https://github.com/auhrs/wrsr-iniconfig/                       (c) 2024 AUHRS")
    print("-" * 80)
    print("\nRENAME EACH ASSET ACCORDING TO BUILDING TYPE")
    print("This option sets the asset name according to the building's type or subtype")
    print("(which is declared in the building.ini). E.g., if the script finds  $TYPE_SHOP ")
    print("the name of the asset in game will be set to Shop. Its folder will be renamed")
    print("ShopNNNNN, where NNNNN is five-digit random number.\n")
    print("You can also set a prefix so it is easier to search the asset ingame.\n")
    print("Set a prefix or press enter for no prefix:")
    prefix = input().strip()

    failed_dirs = []
    success_dirs = []
    log_message = "iniconfig check: Renamed asset according to building type"
    update_log(log_message)
    # Mappings as per your instructions
    type_subtype_names = {
        ('$TYPE_UNIVERSITY', '$SUBTYPE_MEDICAL'): 'Medical University',
        ('$TYPE_UNIVERSITY', '$SUBTYPE_TECHNICAL'): 'Technical University',
        ('$TYPE_UNIVERSITY', '$SUBTYPE_SOVIET'): 'Party HQ',
        ('$TYPE_LIVING', '$SUBTYPE_HOSTEL'): 'Hostel',
        ('$TYPE_BROADCAST', '$SUBTYPE_RADIO'): 'Radio station',
        ('$TYPE_BROADCAST', '$SUBTYPE_TELEVISION'): 'Television station',
        ('$TYPE_STORAGE', '$SUBTYPE_SPACE_FOR_VEHICLES'): 'Vehicle storage',
        ('$TYPE_PRODUCTION_LINE', '$SUBTYPE_ROAD'): 'Vehicle production line',
        ('$TYPE_PRODUCTION_LINE', '$SUBTYPE_AIRPLANE'): 'Aircraft production line',
        ('$TYPE_PRODUCTION_LINE', '$SUBTYPE_RAIL'): 'Locomotive/car production line',
        ('$TYPE_ROADDEPO', '$SUBTYPE_TROLLEYBUS'): 'Trolleybus depot',
        ('$TYPE_ROADDEPO', '$SUBTYPE_TRAM'): 'Tram depot',
        ('$TYPE_RAIL_TRAFO', '$SUBTYPE_ROAD'): 'Trolleybus trafo',
        ('$TYPE_PASSANGER_STATION', '$SUBTYPE_CABLEWAY'): 'Cableway passenger station',
        ('$TYPE_PASSANGER_STATION', '$SUBTYPE_SHIP'): 'Ferry terminal',
        ('$TYPE_PASSANGER_STATION', '$SUBTYPE_AIRPLANE'): 'Airport terminal',
        ('$TYPE_PASSANGER_STATION', '$SUBTYPE_METRO'): 'Metro station',
        ('$TYPE_CARGO_STATION', '$SUBTYPE_CABLEWAY'): 'Cableway cargo station',
        ('$TYPE_CARGO_STATION', '$SUBTYPE_AIRPLANE'): 'Airplane cargo station',
        ('$TYPE_CARGO_STATION', '$SUBTYPE_SHIP'): 'Seaport (experimental)',
        ('$TYPE_ENGINE', '$SUBTYPE_CABLEWAY'): 'Cableway engine',
        ('$TYPE_CONSTRUCTION_OFFICE', '$SUBTYPE_AIRPLANE'): 'Helicopter construction office',
        ('$TYPE_WATER_PUMP', '$SUBTYPE_WATER_SWITCH'): 'Water switch',
        ('$TYPE_TRANSFORMATOR', '$SUBTYPE_PRIORITY_1'): 'Priority switch',
        ('$TYPE_WAITING_STATION', '$SUBTYPE_METRO'): 'Metro end station',
        ('$TYPE_ELETRIC_EXPORT', '$SUBTYPE_OWN_CUSTOM'): 'Custom electric export',
    }

    type_names = {
        '$TYPE_AIRPLANE_GATE': 'Aircraft gate',
        '$TYPE_AIRPLANE_PARKING': 'Aircraft parking',
        '$TYPE_AIRPLANE_TOWER': 'Aircraft tower',
        '$TYPE_ATTRACTION': 'Attraction',
        '$TYPE_BROADCAST': 'Broadcast',
        '$TYPE_CAR_DEALER': 'Car dealer',
        '$TYPE_CARGO_STATION': 'Cargo station',
        '$TYPE_CHURCH': 'Church',
        '$TYPE_CITYHALL': 'City hall',
        '$TYPE_CONSTRUCTION_OFFICE': 'Construction office',
        '$TYPE_CONSTRUCTION_OFFICE_RAIL': 'Rail construction office',
        '$TYPE_CONTAINER_FACILITY': 'Container facility',
        '$TYPE_COOLING_TOWER': 'Cooling tower',
        '$TYPE_COURT_HOUSE': 'Court house',
        '$TYPE_CUSTOMHOUSE': 'Custom house',
        '$TYPE_DEMOLITION_OFFICE': 'Demolition office',
        '$TYPE_DISTRIBUTION_OFFICE': 'Distribution office',
        '$TYPE_DISTRIBUTION_OFFICE_RAIL': 'Rail distribution office',
        '$TYPE_ELETRIC_EXPORT': 'Electric export',
        '$TYPE_ELETRIC_IMPORT': 'Electric import',
        '$TYPE_ENGINE': 'Engine',
        '$TYPE_FACTORY': 'Factory',
        '$TYPE_FARM': 'Farm',
        '$TYPE_FIELD': 'Field',
        '$TYPE_FIRESTATION': 'Fire station',
        '$TYPE_FOREIGN_PIPELINE_EXPORT': 'Foreign pipeline export',
        '$TYPE_FORKLIFT_GARAGE': 'Forklift garage',
        '$TYPE_GARBAGE_OFFICE': 'Garbage office',
        '$TYPE_GAS_STATION': 'Gas station',
        '$TYPE_HEATING_ENDSTATION': 'Heating end station',
        '$TYPE_HEATING_PLANT': 'Heating plant',
        '$TYPE_HEATING_SWITCH': 'Heating switch',
        '$TYPE_HOSPITAL': 'Hospital',
        '$TYPE_HOTEL': 'Hotel',
        '$TYPE_KINDERGARTEN': 'Kindergarten',
        '$TYPE_KINO': 'Cinema',
        '$TYPE_LIVING': 'Residential',
        '$TYPE_MINE_BAUXITE': 'Bauxite mine',
        '$TYPE_MINE_COAL': 'Coal mine',
        '$TYPE_MINE_GRAVEL': 'Gravel mine',
        '$TYPE_MINE_IRON': 'Iron mine',
        '$TYPE_MINE_OIL': 'Oil rig/pumpjack',
        '$TYPE_MINE_URANIUM': 'Uranium mine',
        '$TYPE_MINE_WATER': 'Water pump',
        '$TYPE_MINE_WATER_SURFACE': 'Surface water pump',
        '$TYPE_MINE_WOOD': 'Woodcutter',
        '$TYPE_MONUMENT': 'Monument',
        '$TYPE_ORPHANAGE': 'Orphanage',
        '$TYPE_PARKING': 'Parking',
        '$TYPE_PASSANGER_STATION': 'Passenger station',
        '$TYPE_PEDESTRIAN_BRIDGE': 'Pedestrian bridge',
        '$TYPE_POLICE_STATION': 'Police station',
        '$TYPE_POLLUTION_METER': 'Pollution meter',
        '$TYPE_POWERPLANT': 'Power plant',
        '$TYPE_PRISON': 'Prison',
        '$TYPE_PRODUCTION_LINE': 'Production line',
        '$TYPE_PUB': 'Pub',
        '$TYPE_RAIL_TRAFO': 'Rail transformer',
        '$TYPE_RAILDEPO': 'Rail depot',
        '$TYPE_REPAIR_OFFICE': 'Repair office',
        '$TYPE_ROADDEPO': 'Road depot',
        '$TYPE_SCHOOL': 'School',
        '$TYPE_SCRAPYARD': 'Scrapyard',
        '$TYPE_SECRET_POLICE': 'Secret police',
        '$TYPE_SEWAGE_DISCHARGE': 'Sewage discharge',
        '$TYPE_SEWAGE_ENDSTATION': 'Sewage reservoir',
        '$TYPE_SEWAGE_PUMP': 'Sewage pump',
        '$TYPE_SEWAGE_TREATMENT': 'Sewage treatment',
        '$TYPE_SHIP_DOCK': 'Ship dock',
        '$TYPE_SHOP': 'Shop',
        '$TYPE_SPORT': 'Sport',
        '$TYPE_STORAGE': 'Storage',
        '$TYPE_SUBSTATION': 'Substation',
        '$TYPE_TRAM_GATE': 'Tram gate',
        '$TYPE_TRANSFORMATOR': 'Transformer',
        '$TYPE_TRASH_CONTAINER': 'Trash container',
        '$TYPE_UNIVERSITY': 'University',
        '$TYPE_WAITING_STATION': 'Waiting station',
        '$TYPE_WATER_ENDSTATION': 'Water reservoir',
        '$TYPE_WATER_PUMP': 'Water pump',
        '$TYPE_WATER_SWITCH': 'Water switch',
        '$TYPE_WATER_TREATMENT': 'Water treatment',
    }

    workshopconfig_path = os.path.join(working_directory, 'workshopconfig.ini')

    # Remove lines starting with $OBJECT_BUILDING
    if os.path.exists(workshopconfig_path):
        with open(workshopconfig_path, 'r') as f:
            workshop_lines = f.readlines()
        workshop_lines = [line for line in workshop_lines if not line.startswith('$OBJECT_BUILDING')]
    else:
        workshop_lines = []

    for root, dirs, files in os.walk(working_directory):
        if 'building.ini' in files:
            try:
                building_ini_path = os.path.join(root, 'building.ini')
                backup_name = 'building.{date}.bak'.format(date=datetime.date.today().strftime("%Y%m%d"))
                backup_path = os.path.join(root, backup_name)
                shutil.copy2(building_ini_path, backup_path)

                with open(building_ini_path, 'r') as f:
                    lines = f.readlines()

                # Remove specified lines
                lines = [line for line in lines if not line.startswith((
                    '$COST_WORK', '$COST_RESOURCE', '$NO_LIFESPAN', '$HEATING_DISABLE',
                    '$WATERSEWAGE_DISABLE', '$WASTE_WORKERS_DISABLE', '$WASTE_CUSTOMERS_DISABLE',
                    '$COUNT_LIMIT', '$ELETRIC_WITHOUT_WORKING_FACTOR',
                    '$ELETRIC_WITHOUT_LIGHTING_FACTOR', '$NAME_STR', '$NAME'
                ))]

                # Extract $TYPE and $SUBTYPE
                type_line = next((line for line in lines if line.startswith('$TYPE')), '').strip()
                subtype_line = next((line for line in lines if line.startswith('$SUBTYPE')), '').strip()

                type_value = type_line.split(' ')[0] if type_line else ''
                subtype_value = subtype_line.split(' ')[0] if subtype_line else ''

                if (type_value, subtype_value) in type_subtype_names:
                    type_or_subtype_name = type_subtype_names[(type_value, subtype_value)]
                elif type_value in type_names:
                    type_or_subtype_name = type_names[type_value]
                else:
                    type_or_subtype_name = 'Unknown'

                # Construct $NAME_STR
                if prefix:
                    asset_name = '{} - {}'.format(prefix, type_or_subtype_name)
                else:
                    asset_name = type_or_subtype_name

                # Prepare new building.ini
                new_lines = ['$NAME_STR "{}"\n'.format(asset_name)]
                new_lines += [
                    '$NO_LIFESPAN\n',
                    '$HEATING_DISABLE\n',
                    '$WATERSEWAGE_DISABLE\n',
                    '$WASTE_WORKERS_DISABLE\n',
                    '$WASTE_CUSTOMERS_DISABLE\n',
                    '$COUNT_LIMIT 999\n',
                    '$ELETRIC_WITHOUT_WORKING_FACTOR 1\n',
                    '$ELETRIC_WITHOUT_LIGHTING_FACTOR 1\n'
                ] + lines

                with open(building_ini_path, 'w') as f:
                    f.writelines(new_lines)

                # Rename folder
                random_number = str(random.randint(10000, 99999))
                folder_name = '{}{}'.format(asset_name, random_number)
                folder_name = re.sub(r'\W+', '', folder_name)
                parent_folder = os.path.dirname(root)
                new_folder_path = os.path.join(parent_folder, folder_name)
                os.rename(root, new_folder_path)

                success_dirs.append(os.path.relpath(new_folder_path, working_directory))
            except Exception as e:
                failed_dirs.append((os.path.relpath(root, working_directory), str(e)))

    # Update workshopconfig.ini
    # Remove lines starting with $OBJECT_BUILDING
    if os.path.exists(workshopconfig_path):
        with open(workshopconfig_path, 'r') as f:
            workshop_lines = f.readlines()
        workshop_lines = [line for line in workshop_lines if not line.startswith('$OBJECT_BUILDING')]
    else:
        workshop_lines = []

    # Find index after $VISIBILITY
    visibility_index = None
    for i, line in enumerate(workshop_lines):
        if line.startswith('$VISIBILITY'):
            visibility_index = i + 1
            break
    if visibility_index is None:
        workshop_lines.append('$VISIBILITY\n')
        visibility_index = len(workshop_lines)

    # Add $OBJECT_BUILDING lines
    for dir_name in os.listdir(working_directory):
        dir_path = os.path.join(working_directory, dir_name)
        if os.path.isdir(dir_path):
            workshop_lines.insert(visibility_index, '$OBJECT_BUILDING {}\n'.format(dir_name))
            visibility_index += 1

    with open(workshopconfig_path, 'w') as f:
        f.writelines(workshop_lines)

    display_report(working_directory, success_dirs, failed_dirs)

def rename_assets_individually(working_directory):
    failed_dirs = []
    success_dirs = []
    log_message = "iniconfig check: Renamed asset individually"
    update_log(log_message)

    workshopconfig_path = os.path.join(working_directory, 'workshopconfig.ini')

    # Remove lines starting with $OBJECT_BUILDING
    if os.path.exists(workshopconfig_path):
        with open(workshopconfig_path, 'r') as f:
            workshop_lines = f.readlines()
        workshop_lines = [line for line in workshop_lines if not line.startswith('$OBJECT_BUILDING')]
    else:
        workshop_lines = []

    # Index after $VISIBILITY
    visibility_index = None
    for i, line in enumerate(workshop_lines):
        if line.startswith('$VISIBILITY'):
            visibility_index = i + 1
            break
    if visibility_index is None:
        workshop_lines.append('$VISIBILITY\n')
        visibility_index = len(workshop_lines)

    for root, dirs, files in os.walk(working_directory):
        if 'building.ini' in files:
            try:
                building_ini_path = os.path.join(root, 'building.ini')
                backup_name = 'building.{date}.bak'.format(date=datetime.date.today().strftime("%Y%m%d"))
                backup_path = os.path.join(root, backup_name)
                shutil.copy2(building_ini_path, backup_path)

                with open(building_ini_path, 'r') as f:
                    lines = f.readlines()

                # Extract $NAME_STR or $NAME
                name_line = next((line for line in lines if line.startswith('$NAME_STR') or line.startswith('$NAME')), '').strip()
                if name_line:
                    asset_found = name_line.split(' ', 1)[1].strip('"')
                else:
                    asset_found = 'Unknown'

                # Extract $TYPE and $SUBTYPE
                type_line = next((line for line in lines if line.startswith('$TYPE')), '').strip()
                subtype_line = next((line for line in lines if line.startswith('$SUBTYPE')), '').strip()

                type_value = type_line.split(' ')[0] if type_line else ''
                subtype_value = subtype_line.split(' ')[0] if subtype_line else ''

                # Determine [TYPEORSUBTYPE]
                # Use the same mappings as before
                if (type_value, subtype_value) in type_subtype_names:
                    type_or_subtype_name = type_subtype_names[(type_value, subtype_value)]
                elif type_value in type_names:
                    type_or_subtype_name = type_names[type_value]
                else:
                    type_or_subtype_name = 'Unknown'

                # For this example, ITEM_ID, ITEM_NAME, ITEM_DESC are not extracted
                # Display the screen to the user
                clear_screen()
                print("-" * 80)
                print("WRSR-INICONFIG | https://github.com/auhrs/wrsr-iniconfig/         (c) 2024 AUHRS")
                print("-" * 80)
                print("\nRENAME EACH ASSET INDIVIDUALLY")
                print("Asset found:   {}".format(asset_found))
                print("Type of asset: {}".format(type_or_subtype_name))
                print("Asset ID:      https://steamcommunity.com/sharedfiles/filedetails/?id=")
                print("\nItem:          ")
                print("\nType in the asset's new name below and press ENTER to continue.\n")
                print("Press CTRL+C to cancel all operations")
                print("-" * 80)
                new_name = input("Enter new asset name (suggested: {}): ".format(type_or_subtype_name)).strip()
                if not new_name:
                    new_name = type_or_subtype_name

                # Remove specified lines
                lines = [line for line in lines if not line.startswith((
                    '$COST_WORK', '$COST_RESOURCE', '$NO_LIFESPAN', '$HEATING_DISABLE',
                    '$WATERSEWAGE_DISABLE', '$WASTE_WORKERS_DISABLE', '$WASTE_CUSTOMERS_DISABLE',
                    '$COUNT_LIMIT', '$ELETRIC_WITHOUT_WORKING_FACTOR',
                    '$ELETRIC_WITHOUT_LIGHTING_FACTOR', '$NAME_STR', '$NAME'
                ))]

                # Insert $NAME_STR at the top
                new_lines = ['$NAME_STR "{}"\n'.format(new_name)]
                new_lines += [
                    '$NO_LIFESPAN\n',
                    '$HEATING_DISABLE\n',
                    '$WATERSEWAGE_DISABLE\n',
                    '$WASTE_WORKERS_DISABLE\n',
                    '$WASTE_CUSTOMERS_DISABLE\n',
                    '$COUNT_LIMIT 999\n',
                    '$ELETRIC_WITHOUT_WORKING_FACTOR 1\n',
                    '$ELETRIC_WITHOUT_LIGHTING_FACTOR 1\n'
                ] + lines

                with open(building_ini_path, 'w') as f:
                    f.writelines(new_lines)

                # Rename folder
                random_number = str(random.randint(10000, 99999))
                folder_name = '{}{}'.format(new_name, random_number)
                folder_name = re.sub(r'\W+', '', folder_name)
                parent_folder = os.path.dirname(root)
                new_folder_path = os.path.join(parent_folder, folder_name)
                os.rename(root, new_folder_path)

                # Update workshopconfig.ini
                dir_name = os.path.basename(new_folder_path)
                workshop_lines.insert(visibility_index, '$OBJECT_BUILDING {}\n'.format(dir_name))
                visibility_index += 1

                success_dirs.append(os.path.relpath(new_folder_path, working_directory))
            except Exception as e:
                failed_dirs.append((os.path.relpath(root, working_directory), str(e)))

    # Write updated workshopconfig.ini
    with open(workshopconfig_path, 'w') as f:
        f.writelines(workshop_lines)

    display_report(working_directory, success_dirs, failed_dirs)

def restore_backups(working_directory):
    restored_files = []
    no_backup_dirs = []
    log_message = "iniconfig check: Restored backups"
    update_log(log_message)
    for root, dirs, files in os.walk(working_directory):
        backup_files = [f for f in files if re.match(r'building\.\d{8}\.bak', f)]
        if backup_files:
            for backup_file in backup_files:
                try:
                    backup_path = os.path.join(root, backup_file)
                    building_ini_path = os.path.join(root, 'building.ini')
                    if os.path.exists(building_ini_path):
                        os.remove(building_ini_path)
                    shutil.copy2(backup_path, building_ini_path)
                    date_str = backup_file.split('.')[1]
                    date_formatted = datetime.datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')
                    restored_files.append((date_formatted, os.path.relpath(root, working_directory)))
                    update_log("Restored backup {} as building.ini".format(backup_file))
                except Exception as e:
                    no_backup_dirs.append((os.path.relpath(root, working_directory), str(e)))
        else:
            no_backup_dirs.append((os.path.relpath(root, working_directory), "No backup file found"))
    display_restore_report(working_directory, restored_files, no_backup_dirs)

def display_report(working_directory, success_dirs, failed_dirs):
    clear_screen()
    print("-" * 80)
    print("WRSR-INICONFIG | https://github.com/auhrs/wrsr-iniconfig/         (c) 2024 AUHRS")
    print("-" * 80)
    print("\nREPORT")
    print("You have modified building.ini files in the following directory:")
    print(working_directory + "\n")
    if failed_dirs:
        print("The following directories could not be modified successfully:")
        for dir_info in failed_dirs:
            print("{} (Error: {})".format(dir_info[0], dir_info[1]))
        print()
    if success_dirs:
        print("The following directories were modified successfully:")
        for dir in success_dirs:
            print(dir)
    print("\nPress CTRL+C to cancel all operations")
    print("-" * 80)
    input("Press ENTER to return to the main menu...")

def display_restore_report(working_directory, restored_files, no_backup_dirs):
    clear_screen()
    print("-" * 80)
    print("WRSR-INICONFIG | https://github.com/auhrs/wrsr-iniconfig/         (c) 2024 AUHRS")
    print("-" * 80)
    print("\nREPORT")
    print("You have restored building.ini files in the following directory:")
    print(working_directory + "\n")
    if restored_files:
        print("The following backup files were restored:")
        for date_formatted, folder in restored_files:
            print("Backup date: {}    Folder: {}".format(date_formatted, folder))
        print()
    if no_backup_dirs:
        print("No backup files were found in the following directories:")
        for dir_info in no_backup_dirs:
            print("{} (Error: {})".format(dir_info[0], dir_info[1]))
    print("\nPress CTRL+C to cancel all operations")
    print("-" * 80)
    input("Press ENTER to return to the main menu...")

if __name__ == "__main__":
    main()
