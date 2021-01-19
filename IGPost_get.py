import os
import re
import json
from sys import argv
from urllib.request import Request, urlopen, urlretrieve


def file_ext(isvideo):
    if isvideo:
        return ".mp4"
    else:
        return ".jpg"

def GetPostData(url):
    # set User-Agent to a browser to bypass HTTP 429 response 
    headers = {}
    headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'
    req = Request(url, headers = headers)
    response = urlopen(req)

    if response.status == 200:
        response_content = response.read()
        strcontent = response_content.decode('utf-8')

        p = re.compile('.sharedData = (.*);</script>')
        result = p.search(strcontent)
        if result:
            j = json.loads(result.group(1))
            print ("saving json data...")
            SaveSharedData(j)
            return json.dumps(j)
        else:
            return ""
    else:
        print(f"status: {response.status} |reason: {response.reason}")

def SaveSharedData(jdata):
    owner = jdata["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["owner"]["username"]
    shortcode = jdata["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["shortcode"]

    dirpath = os.path.join(os.getcwd(), "data", owner)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    
    sdata = json.dumps(jdata)

    if not os.path.isfile(dirpath + '/' + shortcode + '.json'):
        with open(dirpath + '/' + shortcode + '.json', 'w') as f: f.write(sdata)
    print ("done.")

def ReadSharedData(sdata, save):
    j = json.loads(sdata)
    owner = j["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["owner"]["username"]
    shortcode = j["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["shortcode"]
    print("owner: " + owner + " | scode: " + shortcode)

    # media type: GraphImage / GraphVideo / GraphSidecar
    if j["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["__typename"] == "GraphSidecar":
        edges = j["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["edge_sidecar_to_children"]["edges"]
        print("media count: " + str(len(edges)))
        for e in edges:
            isvideo = e["node"]["is_video"]
            shortcode = e["node"]["shortcode"]
            if isvideo:
                mediasrc = e["node"]["video_url"]
            else:
                mediasrc = e["node"]["display_resources"][2]["src"]

            print ("\tmediasrc: " + mediasrc[:mediasrc.index("?")])
            print ("\tsave as: " + owner + "/" + shortcode + file_ext(isvideo))
            if save:
                SaveMedia(mediasrc, owner, shortcode + file_ext(isvideo))

    else:
        isvideo = j["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["is_video"]
        if isvideo:
            mediasrc = j["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["video_url"]
        else:
            mediasrc = j["entry_data"]["PostPage"][0]["graphql"]["shortcode_media"]["display_resources"][2]["src"]

        print ("\tmediasrc: " + mediasrc[:mediasrc.index("?")])
        print ("\tsave as: " + owner + "/" + shortcode + file_ext(isvideo))
        if save:
                SaveMedia(mediasrc, owner, shortcode + file_ext(isvideo))

def SaveMedia(mediasrc, owner, filename):
    dirpath = os.path.join(os.getcwd(), "data", owner)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)
    
    filepath = os.path.join(dirpath, filename)
    urlretrieve(mediasrc, filepath)    
    print(mediasrc[:mediasrc.index("?")] + ' saved')

def Main():
    if len(argv) > 1:
        jsondata = GetPostData(str(argv[1]))
        ReadSharedData(jsondata, True)
    else:
        print("IG post URL is not provided")

if __name__ == "__main__": 
    Main()

