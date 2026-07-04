#!/usr/bin/env python3
"""Exporte les 115 notes fréquences existantes au format CHIRP Odmaster TD-H9."""
import os, re, csv, yaml

NOTES_DIR = os.path.join(os.path.dirname(__file__), '..', 'frequences')
OUTPUT = os.path.join(os.path.dirname(__file__), '..', 'exports', 'odmaster-td-h9_115freq.csv')

HEADER = [
    'Location', 'Name', 'Frequency', 'Duplex', 'Offset', 'Tone',
    'rToneFreq', 'cToneFreq', 'DtcsCode', 'DtcsPolarity', 'RxDtcsCode',
    'CrossMode', 'Mode', 'TStep', 'Skip', 'Power', 'Comment',
    'URCALL', 'RPT1CALL', 'RPT2CALL', 'DVCODE'
]

def parse_frontmatter(path):
    """Lit le frontmatter YAML d'une note Obsidian."""
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None
    return yaml.safe_load(match.group(1))

def tone_to_chirp(tone_mode, rx_tone, tx_tone, cross_mode):
    """Convertit nos champs en colonnes CHIRP Tone/rToneFreq/cToneFreq."""
    tm = (tone_mode or '').lower()
    
    if tm == 'tone':
        tone = 'Tone'
        rtone = rx_tone if rx_tone else 88.5
        ctone = tx_tone if tx_tone else 88.5
    elif tm == 'tsql':
        tone = 'TSQL'
        rtone = rx_tone if rx_tone else 88.5
        ctone = rx_tone if rx_tone else 88.5
    else:
        tone = ''
        rtone = 88.5
        ctone = 88.5
    
    # DCS settings - keep defaults since we don't use DCS
    dcs_code = '023'
    dcs_pol = 'NN'
    rx_dcs = '023'
    
    return tone, f"{rtone:.1f}", f"{ctone:.1f}", dcs_code, dcs_pol, rx_dcs

def freq_to_bandwidth(freq, mode):
    """Détermine TStep et Skip selon la bande."""
    if mode and mode.upper() == 'AM':
        return '5.0'
    freq_val = float(freq)
    if freq_val >= 156 and freq_val < 174:
        return '12.5'
    return '5.0'

def power_to_watts(power_str):
    """Normalise la puissance."""
    if not power_str:
        return '2.0W'
    if 'W' in str(power_str):
        p = float(str(power_str).replace('W', ''))
    else:
        p = float(power_str)
    return f"{p:.1f}W"

def main():
    rows = []
    location = 1
    
    for fname in sorted(os.listdir(NOTES_DIR)):
        if not fname.endswith('.md') or fname == '_index.md':
            continue
        
        meta = parse_frontmatter(os.path.join(NOTES_DIR, fname))
        if not meta:
            continue
        
        freq = meta.get('freq', '')
        nom = meta.get('nom', '')
        duplex = meta.get('duplex', 'simplex')
        offset = meta.get('offset', 0.0)
        tone_mode = meta.get('tone_mode', 'none')
        rx_tone = meta.get('rx_tone', 88.5)
        tx_tone = meta.get('tx_tone', 88.5)
        cross_mode = meta.get('cross_mode', 'Tone->Tone')
        mode = meta.get('mode', 'FM')
        power = meta.get('power', '2.0W')
        skip = meta.get('skip', '')
        
        # Duplex et offset
        if duplex == 'simplex' or not duplex:
            ch_duplex = ''
            ch_offset = '0.00000'
        elif duplex == 'plus':
            ch_duplex = '+'
            ch_offset = f"{float(offset):.5f}" if offset else '0.00000'
        elif duplex == 'minus':
            ch_duplex = '-'
            ch_offset = f"{float(offset):.5f}" if offset else '0.00000'
        else:
            ch_duplex = ''
            ch_offset = '0.00000'
        
        # Tone
        tone, rtone, ctone, dcs_code, dcs_pol, rx_dcs = tone_to_chirp(tone_mode, rx_tone, tx_tone, cross_mode)
        
        # Mode
        if mode.upper() == 'NFM':
            ch_mode = 'NFM'
        elif mode.upper() == 'FM':
            ch_mode = 'FM'
        elif mode.upper() == 'AM':
            ch_mode = 'AM'
        elif mode.upper() == 'WFM':
            ch_mode = 'WFM'
        else:
            ch_mode = mode.upper()[:4]
        
        # TStep
        tstep = freq_to_bandwidth(freq, mode)
        
        # Skip
        ch_skip = 'S' if skip else ''
        
        # Power
        ch_power = power_to_watts(power)
        
        # Frequency format
        ch_freq = f"{float(freq):.5f}" if freq else '0.00000'
        
        # Name (truncate to 16 chars for radio display)
        ch_name = (nom or '')[:16]
        
        row = {
            'Location': str(location),
            'Name': ch_name,
            'Frequency': ch_freq,
            'Duplex': ch_duplex,
            'Offset': ch_offset,
            'Tone': tone,
            'rToneFreq': rtone,
            'cToneFreq': ctone,
            'DtcsCode': str(dcs_code),
            'DtcsPolarity': dcs_pol,
            'RxDtcsCode': str(rx_dcs),
            'CrossMode': 'Tone->Tone',
            'Mode': ch_mode,
            'TStep': tstep,
            'Skip': ch_skip,
            'Power': ch_power,
            'Comment': '',
            'URCALL': '',
            'RPT1CALL': '',
            'RPT2CALL': '',
            'DVCODE': ''
        }
        
        rows.append(row)
        location += 1
    
    # Écriture CSV
    os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=HEADER)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"✅ Exporté {len(rows)} canaux vers {OUTPUT}")

if __name__ == '__main__':
    main()