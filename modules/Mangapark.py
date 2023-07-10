import json
from bs4 import BeautifulSoup
from utils.models import Manga

class Mangapark(Manga):
    domain = 'mangapark.to'

    def get_chapters(manga):
        manga = manga.split('-')[0] if '-' in manga else manga
        data = "{\"query\":\"\\n  query get_content_comicChapterRangeList($select: Content_ComicChapterRangeList_Select) {\\n    get_content_comicChapterRangeList(\\n      select: $select\\n    ) {\\n      reqRange{x y}\\n      missing\\n      pager {x y}\\n      items{\\n        serial \\n        chapterNodes {\\n          \\n  id\\n  data {\\n    \\n\\n  id\\n  sourceId\\n\\n  dbStatus\\n  isNormal\\n  isHidden\\n  isDeleted\\n  isFinal\\n  \\n  dateCreate\\n  datePublic\\n  dateModify\\n  lang\\n  volume\\n  serial\\n  dname\\n  title\\n  urlPath\\n\\n  srcTitle srcColor\\n\\n  count_images\\n\\n  stat_count_post_child\\n  stat_count_post_reply\\n  stat_count_views_login\\n  stat_count_views_guest\\n  \\n  userId\\n  userNode {\\n    \\n  id \\n  data {\\n    \\nid\\nname\\nuniq\\navatarUrl \\nurlPath\\n\\nverified\\ndeleted\\nbanned\\n\\ndateCreate\\ndateOnline\\n\\nstat_count_chapters_normal\\nstat_count_chapters_others\\n\\nis_adm is_mod is_vip is_upr\\n\\n  }\\n\\n  }\\n\\n  disqusId\\n\\n\\n  }\\n\\n          sser_read\\n        }\\n      }\\n\\n    }\\n  }\\n  \",\"variables\":{\"select\":{\"comicId\":__comicId__,\"range\":__range__,\"isAsc\":false}},\"operationName\":\"get_content_comicChapterRangeList\"}"
        response = Mangapark.send_request('https://mangapark.to/apo/', headers={'content-type': 'application/json'}, data=data.replace('__range__', 'null').replace('__comicId__', str(manga)), method='POST')
        response_raw = json.loads(response.text)
        end = response_raw['data']['get_content_comicChapterRangeList']['pager'][0]['x']
        begin = response_raw['data']['get_content_comicChapterRangeList']['pager'][-1]['y']
        response = Mangapark.send_request('https://mangapark.to/apo/', headers={'content-type': 'application/json'}, data=data.replace('__range__', f'{{"x":{begin},"y":{end}}}').replace('__comicId__', str(manga)), method='POST')
        response_raw = json.loads(response.text)
        items = response_raw['data']['get_content_comicChapterRangeList']['items']
        chapters = [item['chapterNodes'][0]['data']['urlPath'].split('/')[-1] for item in items[::-1]]
        return chapters

    def get_images(manga, chapter):
        response = Mangapark.send_request(f'https://mangapark.to/title/{manga}/{chapter}')
        soup = BeautifulSoup(response.text, 'html.parser')
        script = soup.find('script', {'id': '__NEXT_DATA__'})
        data = json.loads(script.text)
        images_raw = (data['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']['data']['imageSet'])
        images = [f'{url}?{tail}' for url, tail in zip(images_raw['httpLis'], images_raw['wordLis'])]
        save_names = []
        for i in range(len(images)):
            save_names.append(f'{i+1:03d}.{images[i].split(".")[-1].split("?")[0]}')
        return images, save_names

    def search_by_keyword(keyword, absolute):
        from contextlib import suppress
        page = 1
        prev_page = {}
        while True:
            data = "{\"query\":\"\\n    query get_content_browse_search($select: ComicSearchSelect) {\\n      get_content_browse_search(\\n        select: $select\\n      ) {\\n        reqPage reqSize reqSort reqWord\\n        paging { total pages page size skip }\\n        items {\\n          \\nid\\ndata {\\n  \\n\\nid\\ndbStatus\\nisNormal\\nisHidden\\nisDeleted\\n\\ndateCreate datePublic dateModify\\ndateUpload dateUpdate\\n\\nname\\nslug\\naltNames\\n\\nauthors\\nartists\\ngenres\\n\\noriginalLanguage\\noriginalStatus\\noriginalInfo\\noriginalPubFrom\\noriginalPubTill\\n\\nreadDirection\\n\\nsummary {\\n  code\\n}\\nextraInfo {\\n  code\\n}\\nurlPath\\n\\nurlCover600\\nurlCover300\\nurlCoverOri\\n\\ndisqusId\\n\\n\\n\\nstat_is_hot\\nstat_is_new\\n\\nstat_count_follow\\nstat_count_review \\nstat_count_post_child \\nstat_count_post_reply\\n\\nstat_count_mylists\\n\\nstat_count_vote\\nstat_count_note\\nstat_count_emotions {\\n  field count\\n}\\nstat_count_statuss {\\n  field count\\n}\\nstat_count_scores {\\n  field count\\n}\\nstat_count_views {\\n  field count\\n}\\n\\nstat_score_avg\\nstat_score_bay\\nstat_score_val\\n\\n\\n\\n\\n\\nchart_count_chapters_all\\nchart_count_chapters_bot\\nchart_count_chapters_usr\\n\\nchart_count_serials_all\\nchart_count_serials_bot\\nchart_count_serials_usr\\n\\nchart_count_langs_all\\nchart_count_langs_bot\\nchart_count_langs_usr\\n\\nchart_max_chapterId\\nchart_max_serial_val\\n\\n\\nchart_count_sources_all\\nchart_count_sources_bot\\nchart_count_sources_usr\\n\\nchart_count_lang_to_chapters {field count}\\nchart_count_lang_to_serials {field count}\\n\\n\\nuserId\\nuserNode {\\n  id \\n  data {\\n    \\nid\\nname\\nuniq\\navatarUrl \\nurlPath\\n\\nverified\\ndeleted\\nbanned\\n\\ndateCreate\\ndateOnline\\n\\nstat_count_chapters_normal\\nstat_count_chapters_others\\n\\nis_adm is_mod is_vip is_upr\\n\\n  }\\n}\\n\\nsser_isPageOwner\\nsser_canEditChap\\nsser_canEditInfo\\nsser_canEditPerm\\nsser_canUploadCh\\n\\n\\n}\\n\\n          max_chapterNode {\\n            \\n  id\\n  data {\\n    \\n\\n  id\\n  sourceId\\n\\n  dbStatus\\n  isNormal\\n  isHidden\\n  isDeleted\\n  isFinal\\n  \\n  dateCreate\\n  datePublic\\n  dateModify\\n  lang\\n  volume\\n  serial\\n  dname\\n  title\\n  urlPath\\n\\n  srcTitle srcColor\\n\\n  count_images\\n\\n  stat_count_post_child\\n  stat_count_post_reply\\n  stat_count_views_login\\n  stat_count_views_guest\\n  \\n  userId\\n  userNode {\\n    \\n  id \\n  data {\\n    \\nid\\nname\\nuniq\\navatarUrl \\nurlPath\\n\\nverified\\ndeleted\\nbanned\\n\\ndateCreate\\ndateOnline\\n\\nstat_count_chapters_normal\\nstat_count_chapters_others\\n\\nis_adm is_mod is_vip is_upr\\n\\n  }\\n\\n  }\\n\\n  disqusId\\n\\n\\n  }\\n\\n          }\\n          sser_followed\\n          sser_lastReadChap {\\n            date\\n            chapterNode {\\n              \\n  id\\n  data {\\n    \\n\\n  id\\n  sourceId\\n\\n  dbStatus\\n  isNormal\\n  isHidden\\n  isDeleted\\n  isFinal\\n  \\n  dateCreate\\n  datePublic\\n  dateModify\\n  lang\\n  volume\\n  serial\\n  dname\\n  title\\n  urlPath\\n\\n  srcTitle srcColor\\n\\n  count_images\\n\\n  stat_count_post_child\\n  stat_count_post_reply\\n  stat_count_views_login\\n  stat_count_views_guest\\n  \\n  userId\\n  userNode {\\n    \\n  id \\n  data {\\n    \\nid\\nname\\nuniq\\navatarUrl \\nurlPath\\n\\nverified\\ndeleted\\nbanned\\n\\ndateCreate\\ndateOnline\\n\\nstat_count_chapters_normal\\nstat_count_chapters_others\\n\\nis_adm is_mod is_vip is_upr\\n\\n  }\\n\\n  }\\n\\n  disqusId\\n\\n\\n  }\\n\\n            }\\n          }\\n        }\\n      }\\n    }\\n    \",\"variables\":{\"select\":{\"word\":\"__keyword__\",\"sort\":null,\"page\":__page__,\"incGenres\":[],\"excGenres\":[],\"origLang\":null,\"oficStatus\":null,\"chapCount\":null}},\"operationName\":\"get_content_browse_search\"}"
            response = Mangapark.send_request('https://mangapark.to/apo/', method='POST', headers={'content-type': 'application/json'}, data=data.replace('__keyword__', keyword).replace('__page__', str(page)))
            res_raw = json.loads(response.text)
            mangas = res_raw['data']['get_content_browse_search']['items']
            if mangas == prev_page:
                yield {}
            results = {}
            for manga in mangas:
                name = manga['data']['name']
                url = manga['data']['urlPath'].split('/')[-1]
                authors, artists, genres, status, summary, latest_chapter = '', '', '', '', '', ''
                with suppress(Exception): authors = ', '.join(manga['data']['authors'])
                with suppress(Exception): artists = ', '.join(manga['data']['artists'])
                with suppress(Exception): genres = ', '.join(manga['data']['genres'])
                with suppress(Exception): status = manga['data']['originalStatus']
                with suppress(Exception): summary = manga['data']['summary']['code']
                with suppress(Exception): latest_chapter = manga['max_chapterNode']['data']['urlPath'].split('/')[-1]
                if absolute and keyword.lower() not in name.lower():
                    continue
                results[name] = {
                    'domain': Mangapark.domain,
                    'url': url,
                    'authors': authors,
                    'artists': artists,
                    'genres': genres,
                    'status': status,
                    'summary': summary,
                    'latest_chapter': latest_chapter,
                    'page': page
                }
            yield results
            page += 1
            prev_page = mangas

    def get_db():
        return Mangapark.search_by_keyword('', False)

    def rename_chapter(chapter):
        if chapter in ['pass', None]:
            return ''
        chapter = chapter.split('-')[-1]
        new_name = ''
        reached_number = False
        for ch in chapter:
            if ch.isdigit():
                new_name += ch
                reached_number = True
            elif ch in '-.' and reached_number and new_name[-1] != '.':
                new_name += '.'
        if not reached_number:
            return chapter
        new_name = new_name[:-1] if new_name[-1] == '.' else new_name
        try:
            return f'Chapter {int(new_name):03d}'
        except:
            return f'Chapter {new_name.split(".", 1)[0].zfill(3)}.{new_name.split(".", 1)[1]}'

    def send_request(url, method='GET', headers={}, data={}):
        import requests
        from utils.assets import waiter
        while True:
            try:
                response = requests.get(url) if method == 'GET' else requests.post(url, headers=headers, data=data)
                response.raise_for_status()
                return response
            except (requests.exceptions.HTTPError, requests.exceptions.Timeout) as error:
                raise error
            except requests.exceptions.RequestException:
                waiter()