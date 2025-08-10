"""A python interface for rendering content through Robot Writer.
"""
import requests
import os
import json
from .cache import FileCache
from time import sleep

class RobotWriter(object):
    """
    rw = RobotWriter("http://marple-robotwriter.herokuapp.com", "longandhard123")
    html = rw.render_by_name("test_basic")
    """
    def __init__(self, url, secret):
        self.url = url
        self.secret = secret

    def render_by_name(self, template_name, context, **kwargs):
        """Render a template that is internally avaiable for the robot writer.

        :param context (dict):
        :param template_name: name of template (the pug file)
        """
        template_params = {
            "type": "key",
            "key": template_name,
        }
        return self._render_html(context, template_params, **kwargs)

    def render_string(self, template_str, context, translations=[], **kwargs):
        """
        :param context (dict):
        :param template_str: template content as string (pug syntax)
        :param translations: translation files to be used
        """
        template_params = {
            "type": "string",
            "string": template_str,
        }
        return self._render_html(context, template_params,
                                 translations=translations,
                                 **kwargs)

    def render_from_dropbox(self, template_name, context, **kwargs):
        # Fetch template from dropbox
        dropbox_template_folder = os.environ.get("DROPBOX_TEMPLATE_FOLDER", "/Newsworthy/Artikelmallar")
        dropbox_api_url = os.environ.get("DROPBOX_API_URL", 'https://content.dropboxapi.com/2/files/download')
        required_env_vars = ["DROPBOX_APP_KEY", "DROPBOX_APP_SECRET", "DROPBOX_REFRESH_TOKEN"]
        for prop in required_env_vars:
            if os.environ.get(prop) is None:
                raise RobotWriterError(f"{prop} is not set")

        def get_access_token():
            # Initialize the file-based cache
            cache = FileCache()

            # Use the file-based cache to get the access token
            access_token = cache.get('dropbox_access_token')
            if access_token:
                return access_token

            # fetch fresh access token
            url = "https://api.dropboxapi.com/oauth2/token"
            data = {
                'grant_type': 'refresh_token',
                'refresh_token': os.environ.get("DROPBOX_REFRESH_TOKEN"),
                'client_id': os.environ.get("DROPBOX_APP_KEY"),
                'client_secret': os.environ.get("DROPBOX_APP_SECRET"),
            }

            response = requests.post(url, data=data)
            if response.status_code == 200:
                token_data = response.json()
                access_token = token_data['access_token']
                expires_in = token_data['expires_in']  # I sekunder

                # Cache access token
                cache.set('dropbox_access_token', access_token, timeout=expires_in)
                return access_token
            else:
                raise RobotWriterError(f"Failed to refresh Dropbox access token: {response.json()}")

        access_token = get_access_token()
        dropbox_fp = f"{dropbox_template_folder}/{template_name}.pug"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Dropbox-API-Arg': json.dumps({"path": dropbox_fp})
        }

        # Make the request to download the file
        r = requests.post(dropbox_api_url, headers=headers)

        try:
            r.raise_for_status()
        except:
            raise RobotWriterError(f"Dropbox error, trying to fetch `{dropbox_fp}`:\n{r.text}")
        template_str = r.content.decode('utf-8')
        template_params = {
            "type": "string",
            "string": template_str,
        }
        return self._render_html(context, template_params, **kwargs)

    def _render_html(
            self,
            context,
            template_params,
            translations=None,
            lang="sv",
            theme="newsworthy",
            regenerate_charts=False,
            preview=False,
            retry=False,
            max_retries=3,
            ):
        """Calls the `/html` endpoint.

        :param context (dict): the data that the template will consume (called
            `lead` in the request)
        :param template_params (dict): passed to `template` in the request
        :param translations: a translation dictionary, or the name(s) of one
            or more build-in dicionaries.
        :param lang: Used to select writer templates, 
            and for number formatting, currency symbols, etc.
        :param theme: used to style regenerate_charts
        :param regenerate_charts: force re-generation of charts if they already
            exist.
        :param preview: if true only low resolution charts will be generated
        :param retry: if true, retry the request up to max_retries times when RW API 
        :param max_retries: the number of times to retry the request
        :returns: html as string.
        """
        payload = {
            "lead": context,
            "template": template_params,
            "key": self.secret,
        }
        if translations is not None:
            payload["translations"] = translations

        url = "{base_url}/lead/html?language={lang}&theme={theme}"\
            .format(base_url=self.url, lang=lang, theme=theme)

        if regenerate_charts:
            url += u"&overwrite=true"

        if preview:
            url += u"&preview=true"

        headers = {
            "Accept-Version": "~3"
        }
        def _make_request(url, payload, headers):
            return requests.post(url, json=payload, headers=headers)

        attempt = 0
        html = None
        max_retries = max_retries if retry else 1
        retry_codes = [500, 503]
        while attempt < max_retries:
            try:
                r = _make_request(url, payload, headers)
                r.raise_for_status()
                html = r.content.decode("utf-8")
                break
            except requests.exceptions.HTTPError:
                try:
                    error_resp = r.json()
                    error_resp["status_code"] = r.status_code
                except:
                    # when app is down, the response is not json
                    error_resp = {
                        "message": r.content.decode("utf-8"),
                        "status_code": r.status_code,
                    }

                if r.status_code in retry_codes:
                    attempt += 1
                    if attempt == max_retries:
                        raise RobotWriterError(f"Failed to render template after {max_retries} attempts.\n{error_resp['message']}")
                    sleep(1)
                    continue

                else:
                    msg = f"Error {error_resp['status_code']}: {error_resp['message']}"
                    raise RobotWriterError(msg)

        return html


class RobotWriterError(Exception):
    pass
