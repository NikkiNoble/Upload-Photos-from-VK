import json
import logging
import time
import requests
import PySimpleGUI as sg

TOKEN = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
PATH = 'https://cloud-api.yandex.net:443/v1/disk/resources'


class VKUser:
    def __init__(self, id_of_user):
        self.id_of_user = id_of_user

    def get_photos(self):
        """get information on photos in profile"""
        response = requests.get('https://api.vk.com/method/photos.get', params={
            'owner_id': self.id_of_user,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1,
            'v': 5.21,
            'access_token': TOKEN,
        }
                                )
        return response.json()

    def get_number_of_photos_to_save(self):
        """get information on how many photos to upload"""
        photo_list = self.get_photos()
        count = photo_list['response']['count']
        print(f'Всего фотографий у пользователя: {count}')
        user_response = input('Введите количество фотографий, которое хотите сохранить, либо нажмите '
                              'ENTER(по умолчанию сохранятся 5 фото): ')
        if user_response == '':
            count = 5
        elif int(user_response) > count or int(user_response) < 0:
            print(f'Введено количество больше или меньше, чем есть фотографий. Загрузятся все имеющиеся фото: {count} ')
        else:
            count = int(user_response)
        return count

    def get_link_max_size(self):
        """get dictionary with a link for uploading photos and write json file"""
        dict_of_links = {}
        list_for_file = []
        link = ''
        list_with_inf = []
        try:
            photo_count = self.get_number_of_photos_to_save()
            list_of_photos = self.get_photos()
            for i, photo in enumerate(list_of_photos['response']['items']):
                if i < photo_count:
                    name_of_photo = photo['likes']['count']
                    date = photo['date']
                    height = 0
                    width = 0
                    for photos_inf in photo['sizes']:
                        if i < photo_count:
                            list_with_inf.append(photos_inf)
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
        except KeyError:
            print('Введено что-то не то')
        except ValueError:
            print('Введено что-то не то')
        return dict_of_links


class DiscUser:
    def load_to_disc(self, link_to_upload, code):
        """upload photos to disc"""
        try:
            header = {'Authorization': f'OAuth {code}'}
            requests.put(f'{PATH}?path=photos_fromVK', headers=header)
            count = 0
            for photo_name, link in link_to_upload.items():
                count += 1
                sg.one_line_progress_meter('Photo upload progress', count + 1, len(link_to_upload.items()), '-key-')
                time.sleep(1)
                requests.post(f'{PATH}/upload?path=disk:/photos_fromVK/'
                              f'{str(photo_name) + ".jpg"}&url={link}', headers=header)
                logging.info(f'Загружено {count} фото из {len(link_to_upload.items())}')
                print(f'Загружено {count} фото из {len(link_to_upload.items())}')
            if count == 0:
                print('Фото не загружены')
            else:
                print("Фото успешно загружены на Яндекс Диск.")
        except ValueError:
            print('Введен неправильный токен')


auth_code = input('Введите OAuth-токен для Яндекс Диска: ')
user_id = int(input('Введите id пользователя vkontakte: '))
user = VKUser(user_id)
photo_links = user.get_link_max_size()
user1 = DiscUser()
user1.load_to_disc(photo_links, auth_code)


