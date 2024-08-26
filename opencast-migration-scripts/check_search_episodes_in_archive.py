#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from httpx import BasicAuth, HTTPStatusError

from opencast.archive import get_mediapackage
from opencast.client import OpencastClient
from opencast.info import get_me_json
from opencast.search import get_mediapackages


def main():
    source_opencast_admin_url = 'https://stable.opencast.org'
    source_opencast_presentation_url = 'https://stable.opencast.org'
    source_opencast_username = 'admin'
    source_opencast_password = 'opencast'
    source_auth = BasicAuth(source_opencast_username, source_opencast_password)
    with OpencastClient(source_opencast_admin_url, auth=source_auth,
                        follow_redirects=True) as source_opencast_admin_client:
        with OpencastClient(source_opencast_presentation_url, auth=source_auth,
                            follow_redirects=True) as source_opencast_presentation_client:
            me_json = get_me_json(source_opencast_presentation_client)
            assert 'roles' in me_json
            assert 'ROLE_ADMIN' in me_json.get('roles', [])
            for mp in get_mediapackages(source_opencast_presentation_client):
                # print(f'Found published episode {mp.get_title()} (ID: {mp.get_identifier()}).')
                try:
                    mp_archive = get_mediapackage(source_opencast_admin_client, mp.get_identifier())
                    assert mp.get_identifier() == mp_archive.get_identifier()
                    print(f'Published episode {mp.get_title()} (ID: {mp.get_identifier()}) is in the archive.')
                except HTTPStatusError as e:
                    if e.response.status_code == 404:
                        print(f'ERROR: Published episode {mp.get_title()} (ID: {mp.get_identifier()}) is not archived.')
                    elif e.response.status_code == 403:
                        print(f'ERROR: Access denied for accessing episode {mp.get_title()} '
                              f'(ID: {mp.get_identifier()}).')
                    else:
                        print(f'ERROR: Unable to read episode {mp.get_title()} (ID: {mp.get_identifier()}) '
                              f'from archive. Http statuscode was {e.response.status_code}')
                except:
                    print(f'ERROR: Unable to read episode {mp.get_title()} (ID: {mp.get_identifier()}) '
                          f'from archive.')


if __name__ == '__main__':
    main()
