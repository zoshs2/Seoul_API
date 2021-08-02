#!/Users/yungi/anaconda3/envs/seoul_road/bin/python

# 범용성을 위해서 고쳐야할 부분이 아직 많음.
# This class is still specialized to get access SEOUL_TOPIS API with road_link ID, only.

from config import *
# config.py includes my own confidential info. (TOPIS_SEOUl; dictionary)

class API_Reader:
    def __init__(self):
        self.linkids = []
        self.unknownIDs = []
        self.MY_API_KEY = TOPIS_SEOUL['API_KEY']
        self.BASE_URL = "http://openapi.seoul.go.kr:8088"
        self.API = ['LinkInfo','trafficMlrdLinkInfo','LinkVerInfo','LinkWithLoad']
        self.API_OUTPUT = {'LinkVerInfo':['link_id', 'ver_seq', 'grs80tm_x', 'grs80tm_y'], 'LinkInfo':['link_id', 'road_name', 'st_node_nm', 'ed_node_nm']}
        
    def enroll_slink(self, linkid):
        if hasattr(linkid, '__len__') and (not isinstance(linkid, str)):
            self.linkids = linkid

        else:
            self.linkids = np.array([linkid])
        
        return print("{} ID(s) Succesfully Enrolled".format(len(self.linkids)))

    def url_request(self, api, linkid, startNum=1, endNum=500):
        if api not in self.API:
            raise Exception("Such API is not existed")

        url = self.BASE_URL + "/" + self.MY_OPEN_KEY + "/xml/" + api + "/" + str(startNum) + "/" + str(endNum) + "/" + str(linkid) + "/"
        req = requests.get(url)
        return req

    def parser(self, api) -> pd.DataFrame:
        if len(self.linkids) == 0:
            raise Exception("Fail to enroll road_link ID. Make use of 'enroll_slink(linkid)' method")
        
        data = {}
        for link in tqdm(self.linkids):
            req = self.url_request(api, link)
            html = req.text
            soup = BeautifulSoup(html, 'html.parser')

            status = soup.find_all('message')[0].text
            if "정상 처리되었습니다" != status:
                print("Found a link not matched : {} // Check with 'self.unknownIDs'".format(link))
                self.unknownIDs.append(int(link))
                continue

            for each_attr in self.API_OUTPUT[api]:
                finded_attr = soup.find_all(each_attr)
                if data.get(each_attr) == None:
                    data[each_attr] = [x.text for x in finded_attr]
                else:
                    data[each_attr] = data[each_attr] + [x.text for x in finded_attr]
        
        df = pd.DataFrame(data)
        if 'link_id' in self.API_OUTPUT[api] and not df.empty:
            df['link_id'] = df['link_id'].apply(lambda x: int(x))

        return df