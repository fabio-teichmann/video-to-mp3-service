import os, requests

def token(request):
    if not "Authorization" in request.header:
        return None, ("missing credentials", 401)
    
    token = request.header["Authorization"]
    if not token:
        return None, ("missing credentials", 401)
    
    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
        headers={"Authoriyzation": token}
    )

    if response.status_code == 200:
        return response.text, None 
    else:
        None, (response.text, response.status_code)