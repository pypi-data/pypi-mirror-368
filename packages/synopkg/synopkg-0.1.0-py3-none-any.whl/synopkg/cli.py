# synopkg/cli.py

import argparse

def main():
    parser = argparse.ArgumentParser(description='A Package Manager For Synology by Python3')
    subparsers = parser.add_subparsers(dest='command')

    # 添加 install 命令
    install_parser = subparsers.add_parser('install', help='Install a package')
    install_parser.add_argument('package_name', help='Name of the package to install')

    # 添加 list 命令
    list_parser = subparsers.add_parser('list', help='List installed packages')

    # 添加 update 命令
    update_parser = subparsers.add_parser('update', help='Update a package')
    update_parser.add_argument('package_name', help='Name of the package to update')

    args = parser.parse_args()

    if args.command == 'install':
        print(f'Installing {args.package_name}')
    elif args.command == 'list':
        print('Listing installed packages...')
    elif args.command == 'update':
        print(f'Updating {args.package_name}')

if __name__ == '__main__':
    main()