import os
import stat
import json
import logging
import http.client
import boto3
from avrs.cfg import *
from avrs.launcher_util import *

class AvrsLauncher:
    def __init__(self, parent_parser, cfg):
        self.cfg = cfg
        self.logger = logging.getLogger('avrs')
        provision_parser = parent_parser.add_parser(
            'launcher', 
            help='launcher operations, such as license registration or updating a sim install\n\n')
        sps = provision_parser.add_subparsers(required=True, help='launcher options')

        register_license_psr = sps.add_parser(
            'register-license', 
            help='registers a user license, allowing certain functionaility')
        register_license_psr.add_argument(
            'license_path', 
            help='the path to the license file to register')
        register_license_psr.set_defaults(func=self.register_license)

        license_status_psr = sps.add_parser(
            'license-status', 
            help='shows information related to a user license')
        license_status_psr.set_defaults(func=self.license_status)

        get_latest_psr = sps.add_parser(
            'get-latest-sim-version', 
            help='ask the build info api for the latest sim version')
        get_latest_psr.add_argument("variant", help="which variant to get the latest verison of")
        get_latest_psr.set_defaults(func=self.get_latest_sim_version)

        get_variants_psr = sps.add_parser(
            'list-variants',
            help='lists the available variants of the simulator that can be downloaded')
        get_variants_psr.set_defaults(func=self.get_variants)

        download_sim_psr = sps.add_parser('download-simulator', help='download the simulator')
        download_sim_psr.add_argument('variant', help='which variant of the simulator to download (eg, \"a2rl-iron\" or \"a2rl-humble\")')
        download_sim_psr.add_argument('install_path', help='path to install the simulator')
        download_sim_psr.add_argument('--target-version', default='', help='specify a version other than the most recent to download')
        download_sim_psr.add_argument(
            '--copy-saved-from', 
            default='', 
            help='path to an existing installation from which to copy saved information')
        download_sim_psr.add_argument(
            '--update-existing', 
            action='store_true', 
            help='indicates that the user understands that they are updating an existing installation')
        download_sim_psr.set_defaults(func=self.download_simulator)

    def register_license(self, args):
        print('Trying to Register License File: {}'.format(args.license_path))

        # Load and validate provided license file
        license_ok, license_status, license = validate_license_file(args.license_path)
        if not license_ok:
            print('Error Reading License File: {}'.format(license_status))
            return

        # Cache license info in config
        license_name = os.path.basename(args.license_path)
        self.cfg['license'] = {
            'filename': os.path.basename(license_name),
            'data': license
        }
        save_cfg('avrs', self.cfg)
        print('License Registration Success: {}'.format(self.cfg['license']['filename']))

        # Try to exchange license info for download keys
        print('Retrieving Launcher Download Keys...')
        (dl_keys_ok, dl_keys_status, self.cfg) = try_get_launcher_download_keys(self.cfg)
        if not dl_keys_ok:
            print('Error Getting Launcher Download Keys: {}'.format(dl_keys_status))
            return
        save_cfg('avrs', self.cfg)
        print('Download Key Retrieval Success')

    def license_status(self, args):
        status = get_launcher_license_status_string(self.cfg)
        print('Launcher License Status: {}'.format(status))

    def get_available_sim_versions(self, args):
        pass

        # query something to find out what versions of the sim we can download

    def get_variants(self, args):
        if 'license' not in self.cfg:
            print('no license has been registered\n')
            return

        (dl_keys_ok, dl_keys_status, self.cfg) = try_get_launcher_download_keys(self.cfg)
        if not dl_keys_ok:
            print('Error Getting Launcher Download Keys: {}'.format(dl_keys_status))
            return
        save_cfg('avrs', self.cfg)
        print('{}'.format(self.cfg['variants']))


    def get_latest_sim_version(self, args):
        self.logger.info('getting latest sim version')
        # Validate status of download keys
        dl_keys_ok, dl_keys_status = has_launcher_download_keys(self.cfg)
        if not dl_keys_ok:
            print('Launcher Download Keys Error: {}'.format(dl_keys_status))
            return

        # Get latest build info from API
        build_info_ok, build_info_status, latest_version, staged_version = get_launcher_build_info(
            self.cfg, args.variant)
        if not build_info_ok:
            print('Error Getting Latest Version Info: {}'.format(build_info_status))
            return
        print('{}'.format(latest_version))

    def download_simulator(self, args):

        # update variants before each download. also updates download keys
        print('Updating Variants...')
        self.get_variants(args)

        if args.variant not in self.cfg['variants']:
            print('\"{}\" is not a known variant, try one of: {}'.format(
                args.variant, self.cfg['variants']))
            return

        file_path = args.install_path
        if not os.path.exists(file_path):
            print('Cannot Install Simulator at: {} (Invalid Path, Specify a Directory)'.format(file_path))
            return

        # Validate status of download keys
        dl_keys_ok, dl_keys_status = has_launcher_download_keys(self.cfg)
        if not dl_keys_ok:
            print('Launcher Download Keys Error: {}'.format(dl_keys_status))
            return

        # Get latest build info from API
        build_info_ok, build_info_status, latest_version, staged_version = get_launcher_build_info(
            self.cfg, args.variant)
        if not build_info_ok:
            print('Error Getting Latest Version Info: {}'.format(build_info_status))
            return

        # If we want to copy saved info from another installation
        copy_saved = False
        copy_saved_cache = ''
        if args.copy_saved_from != '':
            if not is_installed_sim(args.copy_saved_from):
                print('The Path: {} Is not an Existing Installation. Cannot Copy Saved'.format(args.copy_saved_from))
                return
            else:
                copy_saved = True

        if copy_saved:
            print('Caching Saved from Existing Installation at: {}'.format(args.copy_saved_from))
            copy_from_saved_dir = os.path.join(args.copy_saved_from, 'Linux', 'Autoverse', 'Saved')
            copy_saved_cache = os.path.join(args.install_path, 'autoverse-saved-cache')
            shutil.copytree(copy_from_saved_dir, copy_saved_cache)

        target_version = latest_version
        if args.target_version == 'staged':
            target_version = staged_version
            print('attempting to download staged version: {}'.format(target_version))
        elif args.target_version != '':  
            target_version = args.target_version
            print('attempting to download specified version: {}'.format(target_version))

        package_zip_name = 'autoverse-linux-{}.zip'.format(target_version)
        package_name = 'autoverse-linux'
        bucket_path = '{}/{}'.format(args.variant, package_zip_name)
        dl_path = os.path.join(args.install_path, package_zip_name)
        unzip_path = os.path.join(args.install_path, package_name)

        if is_installed_sim(unzip_path) and not args.update_existing:
            print('''
Downloading at {} will update an existing installation and override its saved information. 
make sure you have backups of any configuration or use the --copy-saved-from option.
If you are sure, re-run with the --update-existing flag
                '''.format(unzip_path))
            return

        if not is_installed_sim(unzip_path):
            if not 'installs' in self.cfg:
                self.cfg['installs'] = []
            self.cfg['installs'].append(unzip_path)
            save_cfg('avrs', self.cfg)

        print('Downloading {} to {}. This May Take Several Minutes Depending on Connection Speed'.format(bucket_path, dl_path))
        download_simulator_archive(self.cfg, bucket_path, dl_path)

        print('Extracting {} to {}'.format(dl_path, unzip_path))
        shutil.unpack_archive(dl_path, unzip_path)

        if copy_saved:
            print('Migrating Saved Files')
            shutil.copytree(copy_saved_cache, os.path.join(unzip_path, 'Linux', 'Autoverse', 'Saved'), dirs_exist_ok=True)
            shutil.rmtree(copy_saved_cache)

        # Install license if missing
        if not copy_saved:
            print('Installing Registered License: {}'.format(self.cfg['license']['filename']))
            license_install_path = os.path.join(unzip_path, 'Linux', 'Autoverse', 'Saved', self.cfg['license']['filename'])
            with open(license_install_path, 'w', encoding='utf-8') as f:
                json.dump(self.cfg['license']['data'], f, ensure_ascii=False, indent=4)

        # Make Autovers.sh executable
        autoverse_exe = os.path.join(unzip_path, 'Linux', 'Autoverse.sh')
        st = os.stat(autoverse_exe)
        os.chmod(autoverse_exe, st.st_mode | stat.S_IEXEC)

        print('Cleaning up')
        os.remove(dl_path)