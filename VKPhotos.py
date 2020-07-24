import json
import time
import requests
from pip._vendor.progress.bar import IncrementalBar

TOKEN = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
PATH = 'https://cloud-api.yandex.net:443/v1/disk/resources'


class User:

    def get_photos(self, id_of_user):
        """get information on photos in profile"""
        response = requests.get('https://api.vk.com/method/photos.get', params={
            'owner_id': id_of_user,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1,
            'count': 5,
            'v': 5.21,
            'access_token': TOKEN,
        }
                                )
        return response.json()

    def get_link_max_size(self, id_of_user):
        """get dictionary with a link for uploading photos and write json file"""
        dict_of_links = {}
        list_for_file = []
        link = ''
        list_with_inf = []
        list_of_photos = self.get_photos(id_of_user)
        for photo in list_of_photos['response']['items']:
            name_of_photo = photo['likes']['count']
            date = photo['date']
            for photos_inf in photo['sizes']:
                list_with_inf.append(photos_inf)
                height = 0
                width = 0
                if photos_inf['height'] >= height and photos_inf['width'] >= width:
                    height = photos_inf['height']
                    width = photos_inf['width']
                    link = photos_inf['src']
            if name_of_photo in dict_of_links.keys():
                name_of_photo = str(name_of_photo) + '-' + str(date)
                dict_of_links.update({name_of_photo: link})
            else:
                dict_of_links.update({name_of_photo: link})
        for key, value in dict_of_links.items():
            for inf in list_with_inf:
                if value in inf.values():
                    list_for_file.append({'file_name': f'{key}.jpg','size': f'{inf["height"]} x {inf["width"]}'})
        with open('photo_info.json', 'w') as f:
            json.dump(list_for_file, f, indent=False)
        return dict_of_links

    def load_to_disc(self, id_of_user, code):
        """upload photos to disc"""
        header = {'Authorization': f'OAuth {code}'}
        requests.put(f'{PATH}?path=photos_fromVK', headers=header)
        link_to_upload = self.get_link_max_size(id_of_user)
        bar = IncrementalBar('Countdown', max=len(link_to_upload))
        for photo_name, link in link_to_upload.items():
            bar.next()
            time.sleep(1)
            requests.post(f'{PATH}/upload?path=disk:/photos_fromVK/'
                          f'{str(photo_name) + ".jpg"}&url={link}', headers=header)
        bar.finish()
        print("Фото успешно загружены на Яндекс Диск.")


auth_code = input('Введите OAuth-токен для Яндекс Диска: ')
user_id = int(input('Введите id пользователя vkontakte: '))
user = User()
user.load_to_disc(user_id, auth_code)

