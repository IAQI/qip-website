#!/usr/bin/env python3
"""
Generate QIP 2026 schedule files from raw schedule data.

This script:
1. Reads qip2026-schedule-raw.json
2. Reads accepted-papers-2026.json
3. Creates session markdown files in content/2026/sessions/
4. Creates locations-2026.yml
5. Creates schedule-2026.yml
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Optional
import unicodedata


def slugify(text: str) -> str:
    """Convert text to a valid filename slug."""
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text.lower())
    text = re.sub(r'[-\s]+', '_', text)
    return text.strip('_')


def normalize_name(name: str) -> str:
    """Normalize a name by removing diacritics and converting to lowercase."""
    # Normalize unicode characters (NFD = canonical decomposition)
    normalized = unicodedata.normalize('NFD', name)
    # Filter out combining characters (diacritics)
    without_diacritics = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
    result = without_diacritics.lower()

    # Manual exceptions for known name variations
    name_exceptions = {
        'cath': 'catli',  # Çath → Catli
    }

    return name_exceptions.get(result, result)


def extract_last_names(speaker_field) -> List[str]:
    """Extract last names from speaker field (can be string or list)."""
    if isinstance(speaker_field, list):
        # Extract last word from each speaker name and normalize
        return [normalize_name(name.split()[-1]) for name in speaker_field]
    elif isinstance(speaker_field, str):
        return [normalize_name(speaker_field.split()[-1])]
    return []


def match_talk_to_papers(talk: dict, papers: List[dict]) -> List[int]:
    """Match a talk to paper IDs - returns one paper per speaker for multi-speaker talks."""
    # Get individual speakers
    speakers_list = []
    if 'speaker' in talk and talk['speaker']:
        speakers_list.append(talk['speaker'])
    if 'speakers' in talk and isinstance(talk['speakers'], list):
        speakers_list.extend(talk['speakers'])

    if not speakers_list:
        return []

    # For talks with multiple speakers (likely multiple papers), try to match one per speaker
    matched_papers = []
    talk_title = talk.get('title', '').lower()
    common_words = {'a', 'the', 'and', 'or', 'of', 'in', 'on', 'for', 'with', 'to', 'from'}
    talk_words = set(re.findall(r'\w+', talk_title)) - common_words

    for speaker_name in speakers_list:
        speaker_last = normalize_name(speaker_name.split()[-1])
        speaker_full = normalize_name(speaker_name)

        talk_last_names = {speaker_last}
        talk_full_names = {speaker_full}

        best_match = None
        best_score = 0

        for paper in papers:
            # Get paper author last names and full names (normalized)
            paper_last_names = {normalize_name(author['last']) for author in paper.get('authors', [])}
            paper_full_names = {normalize_name(f"{author['first']} {author['last']}") for author in paper.get('authors', [])}

            # Check if any talk speaker matches any paper author
            speaker_match = (talk_last_names & paper_last_names) or (talk_full_names & paper_full_names)

            if speaker_match:
                # Calculate title similarity
                paper_title = paper.get('title', '').lower()
                paper_words = set(re.findall(r'\w+', paper_title)) - common_words

                # Calculate score based on word overlap
                if talk_words and paper_words:
                    overlap = len(talk_words & paper_words)
                    # Score combines title match and speaker match
                    title_score = overlap / len(talk_words) if len(talk_words) > 0 else 0

                    # Bonus points for exact speaker match
                    speaker_match_count = len(talk_last_names & paper_last_names)
                    score = title_score + (speaker_match_count * 0.2)  # Each matching author adds 0.2

                    if score > best_score:
                        best_score = score
                        best_match = paper['pid']

        # Add this speaker's best match if found
        if best_match and best_score > 0:
            matched_papers.append(best_match)

    return matched_papers


def match_plenary_to_papers(session: dict, papers: List[dict]) -> List[int]:
    """Match a plenary session to paper IDs based on speaker names and title similarity."""
    matched_pids = []

    # Get all speakers from the session
    speakers = []
    if 'speaker' in session and session['speaker'] != 'TBC':
        speakers.append(session['speaker'])
    if 'speakers' in session:
        speakers.extend([s for s in session['speakers'] if s != 'TBC'])

    # Get session title for matching
    session_title = session.get('title', '').lower()
    # Remove common prefixes like "Plenary 1:", "Short Plenary 2:", etc.
    session_title = re.sub(r'^(short\s+)?plenary\s+\d+:\s*', '', session_title)
    session_title = re.sub(r'^invited\s+plenary\s*:?\s*', '', session_title)

    # Common words to ignore in title matching
    common_words = {'a', 'the', 'and', 'or', 'of', 'in', 'on', 'for', 'with', 'to', 'from', 'is', 'are'}
    session_words = set(re.findall(r'\w+', session_title)) - common_words

    # For each speaker, find their paper that best matches the title
    for speaker_name in speakers:
        speaker_last = speaker_name.split()[-1].lower()
        speaker_first = speaker_name.split()[0].lower()

        best_match = None
        best_score = 0

        for paper in papers:
            # Check if this speaker is an author of this paper
            is_author = False
            for author in paper.get('authors', []):
                if (author['last'].lower() == speaker_last and
                    author['first'].lower().startswith(speaker_first)):
                    is_author = True
                    break

            if is_author:
                # Calculate title similarity score
                paper_title = paper.get('title', '').lower()
                paper_words = set(re.findall(r'\w+', paper_title)) - common_words

                # Calculate word overlap
                if session_words and paper_words:
                    overlap = len(session_words & paper_words)
                    # Score based on how much of the session title is covered
                    # This works better when session titles are shortened versions
                    score = overlap / len(session_words) if len(session_words) > 0 else 0

                    if score > best_score:
                        best_score = score
                        best_match = paper['pid']

        # Only add if we have a reasonable match (at least 40% of session words in paper title)
        if best_match and best_score >= 0.4:
            matched_pids.append(best_match)

    return matched_pids


def get_session_key(session: dict, track_name: str = None) -> str:
    """Generate a session key/slug."""
    session_type = session.get('type', '')
    title = session.get('title', '')

    if session_type == 'infrastructure':
        # Special sessions like Registration, Coffee Break, etc.
        return '__' + slugify(title)
    elif session_type == 'break':
        return '__' + slugify(title)
    elif session_type == 'social':
        return '__' + slugify(title)
    elif session_type == 'poster':
        return '__poster_session'
    elif session_type == 'tutorial':
        # Extract speaker last name if available
        speaker = session.get('speaker', '')
        if speaker:
            last_name = speaker.split()[-1].lower()
            return f"tutorial_{last_name}"
        return 'tutorial_' + slugify(title)
    elif session_type == 'plenary':
        # Use a combination of day and title
        if 'invited' in title.lower():
            # Will need to number these based on order
            return 'invited_plenary'
        elif 'short' in title.lower():
            # Extract number if present
            match = re.search(r'(\d+)', title)
            if match:
                return f'short_plenary{match.group(1)}'
        return 'plenary'
    elif session_type == 'business':
        return 'business_session'
    elif session_type == 'industry':
        return 'industry_session'
    elif session_type == 'parallel_sessions' and track_name:
        # Use track name
        return slugify(track_name.replace(' ', '_'))

    return slugify(title)


def create_session_file(session_key: str, session_data: dict, year: int, sessions_dir: Path):
    """Create a session markdown file."""
    filepath = sessions_dir / f"{session_key}.md"

    # Prepare front matter
    front_matter = {
        'title': session_data.get('title', ''),
        'format': session_data.get('format', 'contributed'),
        'type': 'sessions',
        'year': year,
        'tags': session_data.get('tags', []),
    }

    # Add optional fields
    if 'speakers' in session_data and session_data['speakers']:
        front_matter['speakers'] = session_data['speakers']

    if 'papers' in session_data and session_data['papers']:
        front_matter['papers'] = session_data['papers']

    front_matter['videoId'] = None
    front_matter['presentation'] = None
    front_matter['draft'] = False

    # Write file
    with open(filepath, 'w') as f:
        f.write('---\n')
        for key, value in front_matter.items():
            if value is None:
                f.write(f'{key}: null\n')
            elif isinstance(value, bool):
                f.write(f'{key}: {str(value).lower()}\n')
            elif isinstance(value, (int, str)):
                if isinstance(value, str) and (':' in value or value.startswith('#')):
                    f.write(f"{key}: '{value}'\n")
                else:
                    f.write(f'{key}: {value}\n')
            elif isinstance(value, list):
                f.write(f'{key}:\n')
                for item in value:
                    f.write(f'  - {item}\n')
        f.write('---\n')

        # Add body content if available
        if 'description' in session_data and session_data['description']:
            f.write(f"\n{session_data['description']}\n")


def main():
    # Paths
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / 'data'
    sessions_dir = base_dir / 'content' / '2026' / 'sessions'

    # Create sessions directory if it doesn't exist
    sessions_dir.mkdir(parents=True, exist_ok=True)

    # Load data
    print("Loading raw schedule...")
    with open(data_dir / 'qip2026-schedule-raw.json') as f:
        schedule_data = json.load(f)

    print("Loading accepted papers...")
    with open(data_dir / 'accepted-papers-2026.json') as f:
        papers = json.load(f)

    # Track all locations and session keys
    all_locations = set()
    schedule_entries = []
    created_sessions = set()

    # Track plenary numbering
    plenary_counters = {}

    print("Processing schedule...")

    for day_data in schedule_data['days']:
        date = day_data['date']
        print(f"\nProcessing {date}...")

        day_sessions = []

        for session in day_data['sessions']:
            session_type = session.get('type', '')

            # Collect locations
            if 'location' in session:
                all_locations.add(session['location'])

            if session_type == 'parallel_sessions':
                # Handle parallel tracks
                for track in session.get('tracks', []):
                    track_name = track['track']
                    location = track.get('location', '')
                    all_locations.add(location)

                    # Determine topic from track name
                    track_lower = track_name.lower()
                    if 'algorithm' in track_lower:
                        topic = 'algorithms'
                    elif 'complexity' in track_lower:
                        topic = 'complexity'
                    elif 'cryptography' in track_lower:
                        topic = 'cryptography'
                    elif 'error correction' in track_lower or 'qec' in track_lower:
                        topic = 'error-correction'
                    elif 'foundation' in track_lower:
                        topic = 'foundations'
                    elif 'information theory' in track_lower or 'inftheory' in track_lower:
                        topic = 'information-theory'
                    elif 'learning' in track_lower or 'tomography' in track_lower:
                        topic = 'learning'
                    elif 'many body' in track_lower or 'manybody' in track_lower:
                        topic = 'many-body'
                    else:
                        topic = 'other'

                    # Create session for this track
                    session_key = get_session_key(session, track_name)

                    if session_key not in created_sessions:
                        # Collect all paper IDs for talks in this track (one per talk)
                        paper_ids = []
                        for talk in track.get('talks', []):
                            matched = match_talk_to_papers(talk, papers)
                            paper_ids.extend(matched)  # Each talk should return 0 or 1 paper

                        # Remove duplicates (should not happen, but just in case)
                        paper_ids = list(dict.fromkeys(paper_ids))

                        # Create session file
                        session_file_data = {
                            'title': track_name,
                            'format': 'contributed',
                            'tags': [topic],
                            'papers': paper_ids,
                        }

                        create_session_file(session_key, session_file_data, 2026, sessions_dir)
                        created_sessions.add(session_key)
                        print(f"  Created session: {session_key} with {len(paper_ids)} papers")

                    # Add to schedule
                    day_sessions.append({
                        'session': session_key,
                        'time': session['time'],
                        'location': location
                    })

            else:
                # Single session
                session_key = get_session_key(session)

                # Handle numbered plenaries
                if session_key in ['invited_plenary', 'plenary']:
                    if session_key not in plenary_counters:
                        plenary_counters[session_key] = 0
                    plenary_counters[session_key] += 1
                    session_key = f"{session_key}{plenary_counters[session_key]}"

                if session_key not in created_sessions:
                    # Determine format and tags
                    if session_type == 'tutorial':
                        format_type = 'tutorial'
                        tags = ['tutorial']
                    elif session_type in ['plenary', 'infrastructure', 'social', 'poster']:
                        format_type = session_type if session_type in ['plenary', 'poster'] else 'other'
                        tags = [session_type]
                    elif session_type == 'break':
                        format_type = 'break'
                        tags = ['other']
                    elif session_type == 'business':
                        format_type = 'other'
                        tags = ['business']
                    elif session_type == 'industry':
                        format_type = 'other'
                        tags = ['industry']
                    else:
                        format_type = 'other'
                        tags = ['other']

                    # Extract speakers if available
                    speakers = []
                    if 'speaker' in session:
                        speaker_name = session['speaker']
                        if speaker_name and speaker_name != 'TBC':
                            # Create speaker key from name
                            speaker_key = slugify(speaker_name.split()[-1])
                            speakers.append(speaker_key)

                    if 'speakers' in session:
                        for speaker_name in session['speakers']:
                            if speaker_name and speaker_name != 'TBC':
                                speaker_key = slugify(speaker_name.split()[-1])
                                speakers.append(speaker_key)

                    session_file_data = {
                        'title': session.get('title', ''),
                        'format': format_type,
                        'tags': tags,
                    }

                    if speakers:
                        session_file_data['speakers'] = speakers

                    # Match plenary sessions to papers
                    if session_type == 'plenary':
                        paper_ids = match_plenary_to_papers(session, papers)
                        if paper_ids:
                            session_file_data['papers'] = paper_ids

                    # Add description for special sessions
                    if session_type == 'tutorial' and 'speaker' in session:
                        # Could add tutorial descriptions here if available
                        pass

                    create_session_file(session_key, session_file_data, 2026, sessions_dir)
                    created_sessions.add(session_key)
                    if session_type == 'plenary' and 'papers' in session_file_data:
                        print(f"  Created session: {session_key} with {len(session_file_data['papers'])} paper(s)")
                    else:
                        print(f"  Created session: {session_key}")

                # Add to schedule
                day_sessions.append({
                    'session': session_key,
                    'time': session['time'],
                    'location': session.get('location', '')
                })

        # Add day to schedule
        schedule_entries.append({
            'day': date,
            'sessions': day_sessions
        })

    # Generate locations-2026.yml
    print("\nGenerating locations-2026.yml...")
    locations_list = []

    # Define location mappings
    location_map = {
        'House of Science': {'key': 'house_of_science', 'label': 'House of Science', 'description': 'University of Latvia'},
        'ATTA Centre': {'key': 'atta_centre', 'label': 'ATTA Centre', 'description': 'Krasta iela 60'},
        'B': {'key': 'room_b', 'label': 'Hall B', 'description': 'ATTA Centre'},
        'A1': {'key': 'room_a1', 'label': 'Hall A1', 'description': 'ATTA Centre'},
        'A2, A3, A4': {'key': 'room_a234', 'label': 'Halls A2, A3, A4', 'description': 'ATTA Centre'},
        'A5': {'key': 'room_a5', 'label': 'Hall A5', 'description': 'ATTA Centre'},
        'Hall 1': {'key': 'hall_1', 'label': 'Hall 1', 'description': 'ATTA Centre'},
        'Hall 4': {'key': 'hall_4', 'label': 'Hall 4', 'description': 'ATTA Centre'},
        'Halls B, C': {'key': 'halls_bc', 'label': 'Halls B, C', 'description': 'ATTA Centre'},
        'Alfa': {'key': 'alfa', 'label': 'Alfa', 'description': 'House of Science'},
        'Delta & Omega': {'key': 'delta_omega', 'label': 'Delta & Omega', 'description': 'House of Science'},
        'Networking Atrium': {'key': 'atrium', 'label': 'Atrium', 'description': 'House of Science'},
        'Startup House Riga': {'key': 'startup_house', 'label': 'Startup House Riga', 'description': ''},
        'Networking B': {'key': 'networking_b', 'label': 'Networking B', 'description': 'ATTA Centre'},
    }

    for loc in sorted(all_locations):
        if loc in location_map:
            locations_list.append(location_map[loc])

    with open(data_dir / 'locations-2026.yml', 'w') as f:
        for loc in locations_list:
            f.write(f"- key: {loc['key']}\n")
            f.write(f"  label: {loc['label']}\n")
            if loc['description']:
                f.write(f"  description: {loc['description']}\n")

    print(f"Created locations-2026.yml with {len(locations_list)} locations")

    # Generate schedule-2026.yml
    print("\nGenerating schedule-2026.yml...")
    with open(data_dir / 'schedule-2026.yml', 'w') as f:
        f.write("# QIP 2026 Conference Schedule\n")
        f.write("# January 24-30, 2026\n")
        f.write("# Riga, Latvia\n\n")

        day_names = ['Saturday', 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

        for i, day_entry in enumerate(schedule_entries):
            date = day_entry['day']

            # Get venue for this day
            day_idx = schedule_data['days'][i]
            venue = day_idx.get('venue', '')
            day_name = day_idx.get('day_name', '')

            f.write(f"# {day_name}, {date.split('-')[1]}/{date.split('-')[2]} - {venue}\n")
            f.write(f"- day: '{date}'\n")
            f.write("  sessions:\n")

            for session in day_entry['sessions']:
                f.write(f"    - session: {session['session']}\n")
                f.write(f"      time: '{session['time']}'\n")
                if session['location']:
                    # Map location to key
                    loc_label = session['location']
                    if loc_label in location_map:
                        loc_key = location_map[loc_label]['key']
                        f.write(f"      location: {loc_key}\n")
                    else:
                        f.write(f"      location: {loc_label}\n")
            f.write("\n")

    print(f"Created schedule-2026.yml with {len(schedule_entries)} days")
    print(f"\nTotal sessions created: {len(created_sessions)}")
    print("\nDone!")


if __name__ == '__main__':
    main()
