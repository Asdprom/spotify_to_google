from gmusicapi import Mobileclient
import spotipy
import spotipy.util as util



username = 'spotify account name/email'
playlist_name = "Imported Music"
client_id = 'your-spotify-client-id-from-app-dashboard'
client_secret='your-spotify-secret-client-id-from-app-dashboard'
redirect_uri='http://localhost:4002'

token = util.prompt_for_user_token(username, 'user-library-read', client_id, client_secret, redirect_uri)

search_strings = []
if token:
    sp = spotipy.Spotify(auth=token)
    page_length = 20
    page = 0

    while True:
        results = sp.current_user_saved_tracks(page_length, page * page_length)
        for item in results['items']:
            track = item['track']
            search_strings.append(
                track['name'] + ' ' + track['artists'][0]['name'])
        if len(results['items']) != page_length:
            break
        else:
            page += 1
else:
    print("Can't get token for", username)

print(f'Detected {len(search_strings)} songs to export.')

mm = Mobileclient()
mm.perform_oauth() 
mm.oauth_login(Mobileclient.FROM_MAC_ADDRESS)
playlist_id = mm.create_playlist(playlist_name)

print(f'Playlist \'{playlist_name}\' created.')
found_songs = 0
for row in search_strings:
    print(f'\t Searching \'{row}\'.')

    search_result = mm.search(row)
    songs = search_result.get('song_hits')

    song_id = None
    if len(songs) > 0:
        song_id = songs[0].get('track').get('storeId')
        found_songs += 1
    else:
        print('Song not found.')
        continue

    mm.add_songs_to_playlist(playlist_id, song_id)

print(f'Imported {found_songs} songs.')
