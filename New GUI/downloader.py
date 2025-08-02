# ================================================================================================================================================================
# Author  : VergePoland (OG Dev), T (New Developer), Cheato (Liberator Dev), Lungu (Shears Dev), SlejmUr (SlejmUr's Downloader), Puppetino (FAQs) Philo (Biography)
# ================================================================================================================================================================

import os
import shutil
import subprocess as sp
import sys
from pathlib import Path

THIS_DIR       = Path(__file__).parent.resolve()
RES_DIR        = THIS_DIR / 'Resources'
TOOLS_DIR      = RES_DIR / 'Tools'
CRACKS_DIR     = RES_DIR / 'Cracks'
DOWNLOADS_DIR  = THIS_DIR / 'Downloads'
MAX_DOWNLOADS  = 25

def run(cmd, **kw) -> int:
    """Run *cmd* (list or str).  Return exit-code, print errors."""
    try:
        return sp.call(cmd, shell=isinstance(cmd, str), **kw)
    except Exception as exc:
        print(f'ERROR while executing: {cmd}\n{exc}')
        return 1

def curl(src_url: str, dst_file: Path):
    """Download *src_url* to *dst_file* with Windows' curl.exe."""
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
    'BlackIce':     ('Y1S1_BlackIce',
                     [('377237', '5188997148801516344'),
                      ('377238', '5362991837480196824'),
                      ('359551', '7932785808040895147')]),
    'DustLine':     ('Y1S2_DustLine',
                     [('377237', '5819137024728546741'),
                      ('377238', '2956768406107766016'),
                      ('359551', '5851804596427790505')]),
    'SkullRain':    ('Y1S3_SkullRain',
                     [('377237', '2303064029242396590'),
                      ('377238', '3040224537841664111'),
                      ('359551', '2206497318678061176')]),
    'RedCrow':      ('Y1S4_RedCrow',
                     [('377237', '3576607363557872807'),
                      ('377238', '912564683190696342'),
                      ('359551', '8569920171217002292')]),
    'VelvetShell':  ('Y2S1_VelvetShell',
                     [('377237', '3576607363557872807'),
                      ('377238', '912564683190696342'),
                      ('359551', '8569920171217002292')]),
    'Health':       ('Y2S2_Health',
                     [('377237', '5875987479498297665'),
                      ('377238', '8542242518901049325'),
                      ('359551', '708773000306432190')]),
    'BloodOrchid':  ('Y2S3_BloodOrchid',
                     [('377237', '6708129824495912434'),
                      ('377238', '4662662335520989204'),
                      ('359551', '1613631671988840841')]),
    'WhiteNoise':   ('Y2S4_WhiteNoise',
                     [('377237', '8748734086032257441'),
                      ('377238', '8421028160473337894'),
                      ('359551', '4221297486420648079')]),
    'Chimera':      ('Y3S1_Chimera',
                     [('377237', '5071357104726974256'),
                      ('377238', '4768963659370299631'),
                      ('359551', '4701787239566783972')]),
    'Parabellum':   ('Y3S2_ParaBellum',
                     [('377237', '6507886921175556869'),
                      ('377238', '7995779530685147208'),
                      ('359551', '8765715607275074515')]),
    'GrimSky':      ('Y3S3_GrimSky',
                     [('377237', '5562094852451837435'),
                      ('377238', '3144556314994867170'),
                      ('359551', '7781202564071310413')]),
    'WindBastion':  ('Y3S4_WindBastion',
                     [('377237', '6502258854032233436'),
                      ('377238', '3144556314994867170'),
                      ('359551', '7659555540733025386')]),
    'BurntHorizon': ('Y4S1_BurntHorizon',
                     [('377237', '8356277316976403078'),
                      ('377238', '3777349673527123995'),
                      ('359551', '5935578581006804383')]),
    'PhantomSight': ('Y4S2_PhantomSight',
                     [('377237', '693082837425613508'),
                      ('377238', '3326664059403997209'),
                      ('359551', '5408324128694463720')]),
    'EmberRise':    ('Y4S3_EmberRise',
                     [('377237', '3546781236735558235'),
                      ('377238', '684480090862996679'),
                      ('359551', '7869081741739849703')]),
    'ShiftingTides':('Y4S4_ShiftingTides',
                     [('377237', '299124516841461614'),
                      ('377238', '510172308722680354'),
                      ('359551', '1842268638395240106')]),
    'VoidEdge':     ('Y5S1_VoidEdge',
                     [('377237', '4736360397583523381'),
                      ('377238', '2583838033617047180'),
                      ('359551', '6296533808765702678')]),
    'SteelWave':    ('Y5S2_SteelWave',
                     [('377237', '4367817844736324940'),
                      ('377238', '5838065097101371940'),
                      ('359551', '893971391196952070')]),
    'ShadowLegacy': ('Y5S3_ShadowLegacy',
                     [('377237', '85893637567200342'),
                      ('377238', '4020038723910014041'),
                      ('359551', '3089981610366186823')]),
    'NeonDawnHM':   ('Y5S4_NeonDawnHM',  # Heated Metal
                     [('377237', '3390446325154338855'),
                      ('377238', '3175150742361965235'),
                      ('359551', '6947060999143280245')]),
    'NeonDawn':     ('Y5S4_NeonDawn',
                     [('377237', '4713320084981112320'),
                      ('377238', '3560446343418579092'),
                      ('359551', '3711873929777458413')]),
    'CrimsonHeist': ('Y6S1_CrimsonHeist',
                     [('377237', '7890853311380514304'),
                      ('377238', '6130917224459224462'),
                      ('359551', '7485515457663576274')]),
    'NorthStar':    ('Y6S2_NorthStar',
                     [('377237', '8733653062998518164'),
                      ('377238', '6767916709017546201'),
                      ('359551', '809542866761090243')]),
    'CrystalGuard': ('Y6S3_CrystalGuard',
                     [('377237', '4859695099882698284'),
                      ('377238', '5161489294178683219'),
                      ('359551', '6526531850721822265')]),
    'HighCalibre':  ('Y6S4_HighCalibre',
                     [('377237', '2637055726475611418'),
                      ('377238', '2074678920289758165'),
                      ('359551', '8627214406801860013')]),
    'DemonVeil':    ('Y7S1_DemonVeil',
                     [('377237', '8323869632165751287'),
                      ('377238', '1970003626423861715'),
                      ('359551', '2178080523228113690')]),
    'VectorGlare':  ('Y7S2_VectorGlare',
                     [('377237', '1363132201391540345'),
                      ('377238', '4500117484519539380'),
                      ('359551', '133280937611742404')]),
    'BrutalSwarm':  ('Y7S3_BrutalSwarm',
                     [('377237', '6425223567680952075'),
                      ('377238', '4623590620762156001'),
                      ('359551', '5906302942203575464')]),
    'SolarRaid':    ('Y7S4_SolarRaid',
                     [('377237', '4466027729495813039'),
                      ('377238', '5107849703917033235'),
                      ('359551', '1819898955518120444')]),
    'CommandingForce': ('Y8S1_CommandingForce',
                     [('377237', '3275824905781062648'),
                      ('377238', '1252692309389076318'),
                      ('359551', '5863062164463920572')]),
    'DreadFactor':  ('Y8S2_DreadFactor',
                     [('377237', '3050554908913191669'),
                      ('377238', '4293396692730784956'),
                      ('359551', '1575870740329742681')]),
    'HeavyMettle':  ('Y8S3_HeavyMettle',
                     [('377237', '2068160275622519212'),
                      ('377238', '2579928666708989224'),
                      ('359551', '3005637025719884427')]),
    'DeepFreeze':   ('Y8S4_DeepFreeze',
                     [('377237', '7646647065987620875'),
                      ('377238', '8339919149418587132'),
                      ('359551', '4957295777170965935')]),
    'DeadlyOmen':   ('Y9S1_DeadlyOmen',
                     [('377237', '1959067516419454682'),
                      ('377238', '1619182300337183882'),
                      ('359551', '1140469899661941149')]),
    'NewBlood':     ('Y9S2_NewBlood',
                     [('377237', '8160812118480939262'),
                      ('377238', '2207285510020603118'),
                      ('359551', '3303120421075579181')]),
    'TwinShells':   ('Y9S3_TwinShells',
                     [('377237', '4296569502001540403'),
                      ('377238', '3038245830342960035'),
                      ('359551', '825321500774263546')]),
    'CollisionPoint': ('Y9S4_CollisionPoint',
                     [('377237', '9207916394092784817'),
                      ('377238', '6303744364362141965'),
                      ('359551', '3039751959139581613')]),
    'PrepPhase':    ('Y10S1_PrepPhase',
                     [('377237', '8382986432868135995'),
                      ('377238', '3364322644809414267'),
                      ('359551', '2619322944995294928')]),
}

TEST_SERVERS = {
    'Steel Wave TS (02/06/20)':     ('Y5S2_SteelWave_ts02_06_20', '1268848856509013057'),
    'Shadow Legacy TS (08/10/20)':  ('Y5S3_ShadowLegacy_ts08_10_20','8833805637802398440'),
    'Ember Rise TS (10/09/19)':     ('Y4S3_EmberRise_ts10_09_19', '8284402568137361637'),
    'Crimson Heist TS (22/02/21)':  ('Y6S1_CrimsonHeist_ts22_02_21', '7921295012062018715'),
    'North Star TS (25/05/21)':     ('Y6S2_NorthStar_ts25_05_21', '6881719580573646381'),
    'Daybreak TS (28/05/25)':       ('Y10S2_Daybreak_ts28_05_25', '5235883268902565724'),
}

K4_TEXTURES = {
    'Vanilla':     ('Y1S0_Vanilla', '8394183851197739981'),
    'Black Ice':   ('Y1S1_BlackIce', '3756048967966286899'),
    'Dust Line':   ('Y1S2_DustLine', '1338949402410764888'),
    'Skull Rain':  ('Y1S3_SkullRain', '3267970968757091405'),
    'Red Crow':    ('Y1S4_RedCrow', '1825939060444887403'),
    'Velvet Shell':('Y2S1_VelvetShell', '3196596628759979362'),
    'Health':      ('Y2S2_Health', '7497579858536910279'),
    'Blood Orchid':('Y2S3_BloodOrchid', '6420469519659049757'),
    'White Noise': ('Y2S4_WhiteNoise', '1118649577165385479'),
    'Chimera':     ('Y3S1_Chimera', '1668513364192382097'),
    'Para Bellum': ('Y3S2_ParaBellum', '204186978012641075'),
    'Grim Sky':    ('Y3S3_GrimSky', '6431001239225997495'),
    'Wind Bastion':('Y3S4_WindBastion', '2243348760021617592'),
    'Burnt Horizon':('Y4S1_BurntHorizon', '3462709886432904855'),
    'Phantom Sight':('Y4S2_PhantomSight', '4107080515154236795'),
    'Ember Rise':  ('Y4S3_EmberRise', '8340682081776225833'),
    'Shifting Tides':('Y4S4_ShiftingTides', '6048763664997452513'),
    'Void Edge':   ('Y5S1_VoidEdge', '2194493692563107142'),
    'Steel Wave':  ('Y5S2_SteelWave', '3257522596542046976'),
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
    """Check if running from OneDrive folder and exit if so."""
    if 'OneDrive' in str(THIS_DIR):
        print("Error: Cannot run from OneDrive folder. Move to different location.")
        return False
    return True

def dotnet_version_ok() -> bool:
    """Check if .NET 9 SDK is installed."""
    try:
        ver = sp.check_output(['dotnet', '--version'],
                              text=True, stderr=sp.DEVNULL).strip()
        return ver.startswith('9.0')
    except Exception:
        return False

def ensure_dotnet():
    """Ensure .NET 9 SDK is available."""
    if not dotnet_version_ok():
        print("Error: .NET 9 SDK not found. Please install it first.")
        print(f"Download from: {URLS['dotnet']}")
        return False
    return True

def ensure_resources():
    """Download and set up required resources."""
    RES_DIR.mkdir(exist_ok=True)
    TOOLS_DIR.mkdir(exist_ok=True)

    if not (RES_DIR / '7z.exe').exists():
        print('Downloading 7-Zip…')
        curl(URLS['7zip'], RES_DIR / '7z.exe')

    if not (RES_DIR / 'DepotDownloader.dll').exists():
        print('Downloading DepotDownloader…')
        tmp = THIS_DIR / 'depot.zip'
        curl(URLS['depotdl'], tmp)
        seven_zip_extract(tmp, RES_DIR)

    if not CRACKS_DIR.exists():
        print('Downloading Cracks…')
        tmp = THIS_DIR / 'cracks.zip'
        curl(URLS['cracks'], tmp)
        seven_zip_extract(tmp, CRACKS_DIR)

    if not (RES_DIR / 'cmdmenusel.exe').exists():
        curl(URLS['cmdMenuSel'], RES_DIR / 'cmdmenusel.exe')

    if not (RES_DIR / 'localization.lang').exists():
        curl(URLS['localization'], RES_DIR / 'localization.lang')

def depot_download(app: str,
                   out_folder: Path,
                   depots: list[tuple[str, str]],
                   username: str,
                   password: str = None):
    """Download depots using DepotDownloader."""
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
            print('\nDownload failed – check credentials or Steam status.')
            return False
    return True

def copy_common_files(dst_folder: Path, cracks_sub: str):
    """Copy common files to destination folder."""
    robocopy(CRACKS_DIR / cracks_sub, dst_folder)
    robocopy(RES_DIR, dst_folder, 'localization.lang', '/IS', '/IT')

def download_season(season_name: str, username: str, password: str = None):
    """Download a specific season."""
    if season_name not in SEASONS:
        print(f"Error: Season '{season_name}' not found.")
        return False
    
    print(f'Downloading {season_name}…')
    folder_name, depots = SEASONS[season_name]
    target = DOWNLOADS_DIR / folder_name
    
    if depot_download('359550', target, depots, username, password):
        cracks_sub = {
            'Y1S0_Vanilla': 'Y1SX-Y6S2',
            'Y1S1_BlackIce': 'Y1SX-Y6S2',
            'Y1S2_DustLine': 'Y1SX-Y6S2',
            'Y1S3_SkullRain': 'Y1SX-Y6S2',
            'Y1S4_RedCrow': 'Y1SX-Y6S2',
            'Y1S5_VelvetShell': 'Y1SX-Y6S2',
        }.get(folder_name, 'Y6S4-Y8SX')
        copy_common_files(target, cracks_sub)
        print('Download Complete!')
        return True
    return False

def download_test_server(ts_name: str, username: str, password: str = None):
    """Download a test server build."""
    if ts_name not in TEST_SERVERS:
        print(f"Error: Test server '{ts_name}' not found.")
        return False
    
    print(f'Downloading {ts_name} Test Server…')
    folder, manifest = TEST_SERVERS[ts_name]
    target = DOWNLOADS_DIR / folder
    
    if depot_download('623990', target, [('623991', manifest)], username, password):
        copy_common_files(target, 'Y1SX-Y6S2')
        print('Download Complete!')
        return True
    return False

def download_4k_textures(name: str, username: str, password: str = None):
    """Download 4K textures for a specific season."""
    if name not in K4_TEXTURES:
        print(f"Error: 4K textures for '{name}' not found.")
        return False
    
    print(f'Downloading 4K Textures for {name}…')
    season_folder, manifest = K4_TEXTURES[name]
    season_path = DOWNLOADS_DIR / season_folder
    
    if depot_download('359550', season_path, [('377239', manifest)], username, password):
        print('Download Complete!')
        return True
    return False

def download_tool(tool_name: str):
    """Download additional tools."""
    tool_map = {
        'liberator': ('R6_Liberator_0.0.0.22.exe', URLS['liberator']),
        'heated_metal_023': ('HeatedMetal.7z', URLS['heated_023']),
        'dxvk': ('Siege-DXVK.zip', URLS['dxvk'])
    }
    
    if tool_name not in tool_map:
        print(f"Error: Tool '{tool_name}' not found.")
        return False
    
    filename, url = tool_map[tool_name]
    
    if tool_name == 'liberator':
        curl(url, TOOLS_DIR / filename)
    elif tool_name == 'heated_metal_023':
        tmp = THIS_DIR / filename
        curl(url, tmp)
        target = (DOWNLOADS_DIR / 'Y5S3_ShadowLegacy'
                  if (DOWNLOADS_DIR / 'Y5S3_ShadowLegacy').exists()
                  else TOOLS_DIR / 'HeatedMetal')
        seven_zip_extract(tmp, target)
    elif tool_name == 'dxvk':
        tmp = THIS_DIR / filename
        curl(url, tmp)
        seven_zip_extract(tmp, TOOLS_DIR / 'Siege-DXVK')
    
    print(f'Tool {tool_name} downloaded successfully!')
    return True

def initialize():
    """Initialize the downloader by checking requirements and setting up resources."""
    if not check_onedrive():
        return False
    if not ensure_dotnet():
        return False
    ensure_resources()
    return True

# Example usage functions:
def get_available_seasons():
    """Get list of available seasons."""
    return list(SEASONS.keys())

def get_available_test_servers():
    """Get list of available test servers."""
    return list(TEST_SERVERS.keys())

def get_available_4k_textures():
    """Get list of available 4K texture packs."""
    return list(K4_TEXTURES.keys())

def get_available_tools():
    """Get list of available tools."""
    return ['liberator', 'heated_metal_023', 'dxvk']