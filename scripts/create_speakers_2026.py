#!/usr/bin/env python3
"""
Create speaker files for QIP 2026 tutorials and plenaries.
Also update session files with correct speaker keys and clean up unused sessions.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Set
import unicodedata


def slugify(text: str) -> str:
    """Convert text to a valid filename slug."""
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '_', text)
    return text.strip('_')


def create_speaker_key(name: str) -> str:
    """Create a speaker key from full name."""
    return slugify(name.replace('.', ''))


def create_speaker_file(speaker_data: dict, speakers_dir: Path, year: int):
    """Create a speaker markdown file."""
    name = speaker_data['name']
    speaker_key = speaker_data['key']
    speaker_type = speaker_data['type']

    # Determine subdirectory based on type
    if speaker_type == 'tutorial':
        subdir = 'tutorial'
    elif speaker_type == 'plenary':
        # Check if it's an invited plenary (TBC speakers) or contributed plenary
        if 'invited' in speaker_data.get('session_title', '').lower():
            subdir = 'invited'
        else:
            subdir = 'plenary'
    else:
        subdir = 'other'

    speaker_dir = speakers_dir / subdir
    speaker_dir.mkdir(parents=True, exist_ok=True)

    # Extract first and last names
    name_parts = name.split()
    if len(name_parts) >= 2:
        surname = name_parts[-1]
        first_name = ' '.join(name_parts[:-1])
    else:
        surname = name
        first_name = name

    filepath = speaker_dir / f"{speaker_key}.md"

    # Don't overwrite existing files
    if filepath.exists():
        print(f"  Skipping {speaker_key} - file already exists")
        return speaker_key

    with open(filepath, 'w') as f:
        f.write('---\n')
        f.write(f'key: {speaker_key}\n')
        f.write(f'name: {name}\n')
        f.write(f'surname: {surname}\n')
        f.write(f'year: {year}\n')
        f.write(f'company: TBD\n')
        f.write(f'photoURL: /{year}/speakers/images/{speaker_key}.png\n')
        f.write(f'type: {subdir}\n')

        if 'title' in speaker_data and speaker_data['title']:
            f.write(f"title: {speaker_data['title']}\n")

        f.write('---\n\n')
        f.write(f'Bio and talk description for {name} to be added.\n')

    print(f"  Created speaker: {speaker_key} ({subdir})")
    return speaker_key


def update_session_file(session_file: Path, speaker_keys: List[str]):
    """Update a session file with correct speaker keys."""
    content = session_file.read_text()

    # Parse front matter
    if not content.startswith('---'):
        return

    parts = content.split('---', 2)
    if len(parts) < 3:
        return

    front_matter = parts[1]
    body = parts[2] if len(parts) > 2 else ''

    # Update speakers field
    lines = front_matter.split('\n')
    new_lines = []
    skip_speakers = False

    for line in lines:
        if line.startswith('speakers:'):
            new_lines.append('speakers:')
            for key in speaker_keys:
                new_lines.append(f'  - {key}')
            skip_speakers = True
        elif skip_speakers and line.startswith('  - '):
            continue  # Skip old speaker entries
        elif skip_speakers and not line.startswith(' '):
            skip_speakers = False
            new_lines.append(line)
        else:
            new_lines.append(line)

    # Write updated content
    new_content = '---\n' + '\n'.join(new_lines) + '\n---' + body
    session_file.write_text(new_content)


def main():
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / 'data'
    speakers_dir = base_dir / 'content' / '2026' / 'speakers'
    sessions_dir = base_dir / 'content' / '2026' / 'sessions'

    # Load raw schedule
    print("Loading raw schedule...")
    with open(data_dir / 'qip2026-schedule-raw.json') as f:
        schedule_data = json.load(f)

    # Load schedule to find which sessions are used
    print("Loading schedule-2026.yml to find used sessions...")
    import yaml
    with open(data_dir / 'schedule-2026.yml') as f:
        schedule_yml = yaml.safe_load(f)

    used_sessions = set()
    for day in schedule_yml:
        for session_entry in day['sessions']:
            used_sessions.add(session_entry['session'])

    # Collect all speakers from raw schedule
    speakers_info = {}

    for day in schedule_data['days']:
        for session in day['sessions']:
            session_type = session.get('type', '')
            session_title = session.get('title', '')

            if session_type in ['plenary', 'tutorial']:
                # Single speaker
                if 'speaker' in session:
                    spk = session['speaker']
                    if spk and spk != 'TBC':
                        key = create_speaker_key(spk)
                        if key not in speakers_info:
                            speakers_info[key] = {
                                'key': key,
                                'name': spk,
                                'type': session_type,
                                'session_title': session_title,
                                'title': session_title
                            }

                # Multiple speakers
                if 'speakers' in session:
                    for spk in session['speakers']:
                        if spk and spk != 'TBC':
                            key = create_speaker_key(spk)
                            if key not in speakers_info:
                                speakers_info[key] = {
                                    'key': key,
                                    'name': spk,
                                    'type': session_type,
                                    'session_title': session_title,
                                    'title': session_title
                                }

    # Create speaker files
    print(f"\nCreating speaker files for {len(speakers_info)} speakers...")
    speaker_keys_map = {}  # Maps name -> key

    for speaker_key, speaker_data in speakers_info.items():
        created_key = create_speaker_file(speaker_data, speakers_dir, 2026)
        speaker_keys_map[speaker_data['name']] = created_key

    # Update session files with correct speaker keys
    print("\nUpdating session files with correct speaker keys...")

    # Map session titles to speaker keys
    session_speakers_map = {}

    for day in schedule_data['days']:
        for session in day['sessions']:
            session_type = session.get('type', '')
            session_title = session.get('title', '')

            if session_type in ['plenary', 'tutorial']:
                speaker_list = []

                if 'speaker' in session and session['speaker'] != 'TBC':
                    speaker_name = session['speaker']
                    if speaker_name in speaker_keys_map:
                        speaker_list.append(speaker_keys_map[speaker_name])

                if 'speakers' in session:
                    for spk in session['speakers']:
                        if spk != 'TBC' and spk in speaker_keys_map:
                            speaker_list.append(speaker_keys_map[spk])

                if speaker_list:
                    # Find matching session file
                    # For tutorials, use tutorial_lastname pattern
                    if session_type == 'tutorial' and speaker_list:
                        # Get the primary speaker's key
                        primary_key = speaker_list[0]
                        session_key = f"tutorial_{primary_key.split('_')[-1]}"
                        session_speakers_map[session_key] = speaker_list

                    # For plenaries, we need to match by the session keys we created
                    # This is trickier - let's update based on session files we find

    # Update tutorial session files
    for session_file in sessions_dir.glob('tutorial_*.md'):
        session_name = session_file.stem
        if session_name in session_speakers_map:
            update_session_file(session_file, session_speakers_map[session_name])
            print(f"  Updated {session_name} with speakers: {session_speakers_map[session_name]}")

    # Also update plenary sessions - read each one and match speakers
    for day in schedule_data['days']:
        for session in day['sessions']:
            if session.get('type') == 'plenary':
                title = session.get('title', '')
                speaker_list = []

                if 'speaker' in session and session['speaker'] != 'TBC':
                    speaker_name = session['speaker']
                    if speaker_name in speaker_keys_map:
                        speaker_list.append(speaker_keys_map[speaker_name])

                if 'speakers' in session:
                    for spk in session['speakers']:
                        if spk != 'TBC' and spk in speaker_keys_map:
                            speaker_list.append(speaker_keys_map[spk])

                if speaker_list:
                    # Find session file by title matching
                    for session_file in sessions_dir.glob('*plenary*.md'):
                        content = session_file.read_text()
                        if f"title: '{title}'" in content or f'title: {title}' in content or f'title: "{title}"' in content:
                            update_session_file(session_file, speaker_list)
                            print(f"  Updated {session_file.stem} with speakers: {speaker_list}")
                            break

    # Clean up unused session files
    print("\nCleaning up unused session files...")
    removed_count = 0

    for session_file in sessions_dir.glob('*.md'):
        session_key = session_file.stem
        if session_key not in used_sessions:
            print(f"  Removing unused session: {session_key}")
            session_file.unlink()
            removed_count += 1

    print(f"\nRemoved {removed_count} unused session files")
    print(f"Total speakers created: {len(speakers_info)}")
    print("\nDone!")


if __name__ == '__main__':
    main()
