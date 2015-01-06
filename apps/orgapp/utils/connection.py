import requests
from yurl import URL

def send_request(target, data):
    """ Sends a single request to the target """

    print("Connecting to\t%s" % target)

    # Parse target again
    t = URL(target)

    # Set own headers
    headers = {'User-Agent' : 'Mozilla 5.10'}

    # Build URL
    url = t.host + t.path

    # Default response
    response = None

    try:
        # Send request
        response = requests.get(
                target,
                headers=headers,
                allow_redirects=False,
                timeout=5
        )

        # Add headers
        for k in response.headers.keys():
            data.append([url, t.port, response.status_code, k, response.headers[k]])

    except Exception:
        import traceback
        print('[ERROR] Exception: ' + traceback.format_exc())

    finally:
        return response
