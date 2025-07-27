# ================================================================================================================================================================
# Author  : VergePoland (OG Dev), T (New Developer), Cheato (Liberator Dev), Lungu (Shears Dev), SlejmUr (SlejmUr's Downloader), Puppetino (FAQs) Philo (Biography)
# ================================================================================================================================================================

import os
import re
import shutil
import subprocess as sp
import sys
import textwrap
import time
import webbrowser
from pathlib import Path

THIS_DIR       = Path(__file__).parent.resolve()
RES_DIR        = THIS_DIR / 'Resources'
TOOLS_DIR      = RES_DIR / 'Tools'
CRACKS_DIR     = RES_DIR / 'Cracks'
DOWNLOADS_DIR  = THIS_DIR / 'Downloads'
MAX_DOWNLOADS  = 25         
COLOR_RESET    = '\x1b[0m'
COLOR_MENU     = '\x1b[1;97m' 
COLOR_HILITE   = '\x1b[1;92m' 

def clear(): os.system('cls' if os.name == 'nt' else 'clear')

def pause(msg: str = 'Press any key to continue…'):
    os.system(f'pause > nul') if os.name == 'nt' else input(msg)

def run(cmd, **kw) -> int:
    """Run *cmd* (list or str).  Return exit-code, print errors."""
    try:
        return sp.call(cmd, shell=isinstance(cmd, str), **kw)
    except Exception as exc:
        print(f'ERROR while executing: {cmd}\n{exc}')
        pause()
        return 1

def curl(src_url: str, dst_file: Path):
    """Download *src_url* to *dst_file* with Windows’ curl.exe."""
    dst_file.parent.mkdir(parents=True, exist_ok=True)
    print(f'\nDownloading:\n  {src_url}\ninto\n  {dst_file}')
    cmd = ['curl', '-L', src_url, '--ssl-no-revoke', '--output', str(dst_file)]
    if run(cmd) != 0:
        sys.exit('Download failed, aborting.')

def seven_zip_extract(archive: Path, out_dir: Path):
    exe = RES_DIR / '7z.exe'
    if not exe.exists():
        sys.exit('7z.exe missing – resources not prepared correctly.')
    cmd = [str(exe), 'x', '-y', f'-o{out_dir}', str(archive), '-aoa']
    if run(cmd) != 0:
        sys.exit('7-Zip extraction failed.')
    archive.unlink(missing_ok=True)

def robocopy(src: Path, dst: Path, *extra_args: str):
    if os.name == 'nt':
        cmd = ['Robocopy', str(src), str(dst)] + list(extra_args)
        run(cmd, stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    else:
        if src.is_dir():
            shutil.copytree(src, dst, dirs_exist_ok=True)
        elif src.is_file():
            shutil.copy2(src, dst)

# DATA TABLES – Seasons / Test-servers / 4K-packs 
SEASONS = {
    'Vanilla':      ('Y1S0_Vanilla',
                     [('377237', '8358812283631269928'),
                      ('377238', '6835384933146381100'),
                      ('359551', '3893422760579204530')]),
    'BlackIce':    ('Y1S1_BlackIce',
                     [('377237', '5188997148801516344'),
                      ('377238', '5362991837480196824'),
                      ('359551', '7932785808040895147')]),
    'DustLine':    ('Y1S2_DustLine',
                     [('377237', '5819137024728546741'),
                      ('377238', '2956768406107766016'),
                      ('359551', '5851804596427790505')]),
    'SkullRain':    ('Y1S3_SkullRain',
                     [('377237', '2303064029242396590'),
                      ('377238', '3040224537841664111'),
                      ('359551', '2206497318678061176')]),
    'RedCrow':    ('Y1S4_RedCrow',
                     [('377237', '3576607363557872807'),
                      ('377238', '912564683190696342'),
                      ('359551', '8569920171217002292')]),
    'VelvetShell':    ('Y2S1_VelvetShell',
                     [('377237', '3576607363557872807'),
                      ('377238', '912564683190696342'),
                      ('359551', '8569920171217002292')]),
    'Health':         ('Y2S2_Health',
                     [('377237', '5875987479498297665'),
                      ('377238', '8542242518901049325'),
                      ('359551', '708773000306432190')]),
    'BloodOrchid':    ('Y2S3_BloodOrchid',
                     [('377237', '6708129824495912434'),
                      ('377238', '4662662335520989204'),
                      ('359551', '1613631671988840841')]),
    'WhiteNoise':    ('Y2S4_WhiteNoise',
                     [('377237', '8748734086032257441'),
                      ('377238', '8421028160473337894'),
                      ('359551', '4221297486420648079')]),
    'Chimera':    ('Y3S1_Chimera',
                     [('377237', '5071357104726974256'),
                      ('377238', '4768963659370299631'),
                      ('359551', '4701787239566783972')]),
    'Parabellum':    ('Y3S2_ParaBellum',
                     [('377237', '6507886921175556869'),
                      ('377238', '7995779530685147208'),
                      ('359551', '8765715607275074515')]),
    'Grimsky':    ('Y3S3_GrimSky',
                     [('377237', '5562094852451837435'),
                      ('377238', '3144556314994867170'),
                      ('359551', '7781202564071310413')]),
    'WindBastion':    ('Y3S4_WindBastion',
                     [('377237', '6502258854032233436'),
                      ('377238', '3144556314994867170'),
                      ('359551', '7659555540733025386')]),
    'BurntHorizon':    ('Y4S1_BurntHorizon',
                     [('377237', '8356277316976403078'),
                      ('377238', '3777349673527123995'),
                      ('359551', '5935578581006804383')]),
    'PhantomSight':    ('Y4S2_PhantomSight',
                     [('377237', '693082837425613508'),
                      ('377238', '3326664059403997209'),
                      ('359551', '5408324128694463720')]),
    'EmberRise':    ('Y4S3_EmberRise',
                     [('377237', '3546781236735558235'),
                      ('377238', '684480090862996679'),
                      ('359551', '7869081741739849703')]),
    'ShiftingTides':    ('Y4S4_ShiftingTides',
                     [('377237', '299124516841461614'),
                      ('377238', '510172308722680354'),
                      ('359551', '1842268638395240106')]),
    'VoidEdge':    ('Y5S1_VoidEdge',
                     [('377237', '4736360397583523381'),
                      ('377238', '2583838033617047180'),
                      ('359551', '6296533808765702678')]),
}
TEST_SERVERS = {
    'Steel Wave TS (02/06/20)':  ('Y5S2_SteelWave_ts02_06_20', '1268848856509013057'),
    'Shadow Legacy TS (08/10/20)': ('Y5S3_ShadowLegacy_ts08_10_20','8833805637802398440'),
}
K4_TEXTURES = {
    'Vanilla':     ('Y1S0_Vanilla', '8394183851197739981'),
    'Black Ice':   ('Y1S1_BlackIce', '3756048967966286899'),
}

URLS = {
    'dotnet':  'https://builds.dotnet.microsoft.com/dotnet/Sdk/9.0.302/'
               'dotnet-sdk-9.0.302-win-x64.exe',
    '7zip':    'https://github.com/DataCluster0/R6TBBatchTool/raw/master/Requirements/7z.exe',
    'depotdl': 'https://github.com/SteamRE/DepotDownloader/releases/download/'
               'DepotDownloader_3.4.0/DepotDownloader-framework.zip',
    'cracks':  'https://github.com/Vergepoland/r6-downloader/raw/refs/heads/main/Cracks.zip',
    'cmdMenuSel': 'https://github.com/SlejmUr/R6-AIOTool-Batch/raw/master/Requirements/cmdmenusel.exe',
    'localization':'https://github.com/Vergepoland/r6-downloader/raw/refs/heads/main/localization.lang',
    'liberator':  'https://github.com/SlejmUr/Manifest_Tool_TB/raw/main/R6_Liberator_0.0.0.22.exe',
    'heated_023': 'https://github.com/DataCluster0/HeatedMetal/releases/download/0.2.3/HeatedMetal.7z',
    'dxvk':       'https://github.com/Vergepoland/r6-downloader/raw/refs/heads/main/Siege-DXVK.zip',
}


def check_onedrive():
    if 'OneDrive' in str(THIS_DIR):
        webbrowser.open('https://shorturl.at/qk3SX')
        clear()
        print(textwrap.dedent('''
        ----------------------------------------------------------------------------
        You ran this downloader inside of a OneDrive folder.
        Move the downloader to a different location!
        Follow this guide if you need help:  https://shorturl.at/qk3SX
        ----------------------------------------------------------------------------'''))
        pause()
        sys.exit()

def dotnet_version_ok() -> bool:
    try:
        ver = sp.check_output(['dotnet', '--version'],
                              text=True, stderr=sp.DEVNULL).strip()
        return ver.startswith('9.0')
    except Exception:
        return False

def ensure_dotnet():
    if dotnet_version_ok():
        return
    webbrowser.open(URLS['dotnet'])
    clear()
    print(textwrap.dedent('''
    ------------------------------------------------------------------------------
    Couldn't find .NET 9 SDK – please download & install it before continuing!
    dotnet --version / dotnet --list-sdks shown below for debugging:
    ------------------------------------------------------------------------------'''))
    run('dotnet --version')
    run('dotnet --list-sdks')
    pause()
    sys.exit()

def ensure_resources():
    RES_DIR.mkdir(exist_ok=True)
    TOOLS_DIR.mkdir(exist_ok=True)

    if not (RES_DIR / '7z.exe').exists():
        clear(); print('Downloading 7-Zip…')
        curl(URLS['7zip'], RES_DIR / '7z.exe')

    if not (RES_DIR / 'DepotDownloader.dll').exists():
        clear(); print('Downloading DepotDownloader…')
        tmp = THIS_DIR / 'depot.zip'
        curl(URLS['depotdl'], tmp)
        seven_zip_extract(tmp, RES_DIR)

    if not CRACKS_DIR.exists():
        clear(); print('Downloading Cracks…')
        tmp = THIS_DIR / 'cracks.zip'
        curl(URLS['cracks'], tmp)
        seven_zip_extract(tmp, CRACKS_DIR)

    if not (RES_DIR / 'cmdmenusel.exe').exists():
        curl(URLS['cmdMenuSel'], RES_DIR / 'cmdmenusel.exe')

    if not (RES_DIR / 'localization.lang').exists():
        curl(URLS['localization'], RES_DIR / 'localization.lang')


def choose(title: str, options: list[str]) -> int:
    """
    Console menu.
    Returns index (1-based) matching Batch script convention.
    """
    clear()
    print(COLOR_MENU + title + COLOR_RESET)
    for i, opt in enumerate(options, 1):
        print(f' {COLOR_HILITE}{i:2d}{COLOR_RESET} – {opt}')
    while True:
        try:
            sel = int(input('\nSelect > '))
            if 1 <= sel <= len(options):
                return sel
        except ValueError:
            pass
        print('Invalid selection – try again.')


import getpass

def ask_credentials() -> tuple[str, str]:
    user = input('Enter Steam Username: ')
    pwd = getpass.getpass('Enter Steam Password (or --remember-password): ')
    return user, pwd



def depot_download(app: str,
                   out_folder: Path,
                   depots: list[tuple[str, str]],
                   username: str,
                   password: str = None):
    out_folder.mkdir(parents=True, exist_ok=True)
    for depot_id, manifest in depots:
        cmd = [
            'dotnet', str(RES_DIR / 'DepotDownloader.dll'),
            '-app', app,
            '-depot', depot_id,
            '-manifest', manifest,
            '-username', username,
            '-dir', str(out_folder),
            '-validate',
            '-max-downloads', str(MAX_DOWNLOADS)
        ]
        if password:
            if password == '--remember-password':
                cmd.append('-remember-password')
            else:
                cmd += ['-password', password]

        if run(cmd) != 0:
            print('\nDownload aborted – check credentials or Steam status.')
            pause()
            return False
    return True


def copy_common_files(dst_folder: Path, cracks_sub: str):
    robocopy(CRACKS_DIR / cracks_sub, dst_folder)
    robocopy(RES_DIR, dst_folder, 'localization.lang', '/IS', '/IT')

def download_season(season_name: str):
    clear()
    print(f'Downloading {season_name}…')
    folder_name, depots = SEASONS[season_name]
    target = DOWNLOADS_DIR / folder_name
    user, pwd = ask_credentials()
    if depot_download('359550', target, depots, user, pwd):
        cracks_sub = {
            'Y1S0_Vanilla'     : 'Y1SX-Y6S2',
            'Y1S1_BlackIce'    : 'Y1SX-Y6S2',
            'Y1S2_DustLine'     : 'Y1SX-Y6S2',
            'Y1S3_SkullRain'    : 'Y1SX-Y6S2',
            'Y1S4_RedCrow'     : 'Y1SX-Y6S2',
            'Y1S5_VelvetShell'    : 'Y1SX-Y6S2',
        }.get(folder_name, 'Y6S4-Y8SX')
        copy_common_files(target, cracks_sub)
        download_complete()


def download_test_server(ts_name: str):
    clear()
    print(f'Downloading {ts_name} Test Server…')
    folder, manifest = TEST_SERVERS[ts_name]
    target = DOWNLOADS_DIR / folder
    user, _ = ask_credentials()
    if depot_download('623990', target, [('623991', manifest)], user):
        copy_common_files(target, 'Y1SX-Y6S2')
        download_complete()

def download_4k(name: str):
    clear()
    print(f'Downloading 4K Textures for {name}…')
    season_folder, manifest = K4_TEXTURES[name]
    season_path = DOWNLOADS_DIR / season_folder
    user, _ = ask_credentials()
    depot_download('359550', season_path, [('377239', manifest)], user)
    download_complete()


def download_warning():
    clear()
    print(textwrap.dedent('''
    --------------------------------------------------------------------------------
      PLEASE ENSURE YOU HAVE AN ANTIVIRUS EXCLUSION SET UP BEFORE CONTINUING!!
      THE DOWNLOADER AND GAME WILL MALFUNCTION OTHERWISE!
    --------------------------------------------------------------------------------'''))
    time.sleep(10)

def download_complete():
    clear()
    print('\n-------------------------\n  Download Complete!  \n-------------------------')
    pause()


def extra_tools_menu():
    while True:
        sel = choose('Extra Tools Download', [
            '<- Back to Main Menu',
            'Refresh Menu',
            'Download Liberator (Y1S0 – Y4S4)',
            'Download Heated Metal 0.2.3 (Y5S3 ONLY)',
            'Download Heated Metal latest version (Y5S4 ONLY)',
            'Download DXVK (Vulkan Renderer)'
        ])
        if sel == 1: return
        if sel == 2: continue
        if sel == 3:
            curl(URLS['liberator'], TOOLS_DIR / 'R6_Liberator_0.0.0.22.exe')
            pause()
        elif sel == 4:
            tmp = THIS_DIR / 'HeatedMetal.7z'
            curl(URLS['heated_023'], tmp)
            target = (DOWNLOADS_DIR / 'Y5S3_ShadowLegacy'
                      if (DOWNLOADS_DIR / 'Y5S3_ShadowLegacy').exists()
                      else TOOLS_DIR / 'HeatedMetal')
            seven_zip_extract(tmp, target)
            pause()
        elif sel == 5:
            webbrowser.open('https://github.com/DataCluster0/HeatedMetal/releases/latest')
            pause()
        elif sel == 6:
            tmp = THIS_DIR / 'Siege-DXVK.zip'
            curl(URLS['dxvk'], tmp)
            seven_zip_extract(tmp, TOOLS_DIR / 'Siege-DXVK')
            pause()

def toggle_speed():
    global MAX_DOWNLOADS
    MAX_DOWNLOADS = 50 if MAX_DOWNLOADS == 25 else 25


def open_guide():
    webbrowser.open('https://puppetino.github.io/Throwback-FAQ')

def open_faq():
    clear()
    print(textwrap.dedent('''\
        -------------------------------------------------------------------------
        FAQ
        -------------------------------------------------------------------------
        Q: Is it safe to enter my password?
        A: Yes. DepotDownloader source code is public.

        Q: Why do I get 'Invalid Password'?
        A: Use your LEGACY Steam username (the one you log in with).

        Q: Why does it say 'Download Complete' immediately?
        A: Could not connect to Steam in 3-5 attempts – try again.

        Q: Why can't I see my password typing?
        A: Security measure.
        -------------------------------------------------------------------------'''))
    pause()


def main_menu():
    download_warning()
    while True:
        sel = choose('Ts Downloader', [
            'Game Downloader',
            'Test Server Downloader',
            '4K Textures Download',
            'Modding / Extra Tools',
            'Claim Siege on Steam for free',
            'Downloader Settings',
            'Installation Guide and FAQ'
        ])
        if sel == 1: game_downloader_menu()
        elif sel == 2: test_server_menu()
        elif sel == 3: textures_menu()
        elif sel == 4: extra_tools_menu()
        elif sel == 5: webbrowser.open('https://store.steampowered.com/app/359550')
        elif sel == 6: settings_menu()
        elif sel == 7: guide_faq_menu()

def game_downloader_menu():
    seasons = ['<- Back to Main', 'Refresh'] + list(SEASONS.keys())
    while True:
        idx = choose('Game Downloader – choose season', seasons)
        if idx == 1: return
        if idx == 2: continue
        season_name = seasons[idx-1]
        download_season(season_name)

def test_server_menu():
    opts = ['<- Back to Main', 'Refresh'] + list(TEST_SERVERS.keys())
    while True:
        idx = choose('Test Server Downloader', opts)
        if idx == 1: return
        if idx == 2: continue
        ts_name = opts[idx-1]
        download_test_server(ts_name)

def textures_menu():
    opts = ['<- Back to Main', 'Refresh'] + list(K4_TEXTURES.keys())
    while True:
        idx = choose('4K Textures Downloader', opts)
        if idx == 1: return
        if idx == 2: continue
        name = opts[idx-1]
        download_4k(name)

def settings_menu():
    while True:
        sel = choose('Downloader Settings',
                     ['<- Back', f'Set faster download speed '
                                 f'(Current = {MAX_DOWNLOADS})'])
        if sel == 1: return
        if sel == 2:
            toggle_speed()

def guide_faq_menu():
    while True:
        sel = choose('Guide & FAQ',
                     ['<- Back', 'Refresh', 'Throwback Guide & FAQ (UPDATED)',
                      'Downloader FAQ'])
        if sel == 1: return
        if sel == 2: continue
        if sel == 3: open_guide()
        if sel == 4: open_faq()

def main():
    check_onedrive()
    ensure_dotnet()
    ensure_resources()
    main_menu()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nAborted by user.')