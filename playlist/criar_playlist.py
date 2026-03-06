#!/usr/bin/env python3
"""
Cria a playlist "Clássicos 1936–1956 — Para a Vovó" no Spotify.

Pré-requisitos:
  pip install spotipy

Configuração:
  1. Acesse https://developer.spotify.com/dashboard
  2. Crie um app (nome qualquer)
  3. Em "Edit Settings", adicione o Redirect URI: http://localhost:8888/callback
  4. Copie o Client ID e Client Secret para as variáveis abaixo
"""

import re
import spotipy
from spotipy.oauth2 import SpotifyOAuth

# ─── CONFIGURAÇÃO ────────────────────────────────────────────────────────────
CLIENT_ID     = "85fe52cff756410095a3714c028c288b"
CLIENT_SECRET = "822d085d81af4aae9ad800609dcc3706"
REDIRECT_URI  = "http://127.0.0.1:8888/callback"
PLAYLIST_NAME = "Clássicos 1936–1956 — Para a Vovó 🎶"
PLAYLIST_DESC = "Uma viagem musical pela época em que Maria Venâncio nasceu. Brasil e mundo, de 1936 a 1956."
# ─────────────────────────────────────────────────────────────────────────────

PLAYLIST_FILE = "playlist.txt"

def extract_track_ids(filepath):
    ids = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            match = re.search(r"open\.spotify\.com/track/([A-Za-z0-9]+)", line)
            if match:
                ids.append("spotify:track:" + match.group(1))
    return ids

def main():
    track_uris = extract_track_ids(PLAYLIST_FILE)
    print(f"Faixas encontradas: {len(track_uris)}")

    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="playlist-modify-public",
    ))

    me = sp.me()
    user_id = me["id"]
    print(f"Autenticado como: {me['display_name']}")

    # Procura playlist existente com o mesmo nome
    playlist = None
    results = sp.current_user_playlists()
    while results:
        for item in results["items"]:
            if item["name"] == PLAYLIST_NAME:
                playlist = item
                break
        if playlist or not results["next"]:
            break
        results = sp.next(results)

    if playlist:
        print(f"Playlist existente encontrada, atualizando...")
        # Limpa todas as faixas atuais
        sp.playlist_replace_items(playlist["id"], [])
    else:
        print(f"Criando nova playlist...")
        playlist = sp.user_playlist_create(
            user=user_id,
            name=PLAYLIST_NAME,
            public=True,
            description=PLAYLIST_DESC,
        )

    # A API aceita no máximo 100 faixas por chamada
    for i in range(0, len(track_uris), 100):
        sp.playlist_add_items(playlist["id"], track_uris[i:i+100])

    print(f"✅ {len(track_uris)} músicas adicionadas com sucesso! (upsert)")
    print(f"🔗 {playlist['external_urls']['spotify']}")

if __name__ == "__main__":
    main()
