from pathlib import Path
from threading import Thread, Semaphore
from making_with_code_cli.mwc_accounts_api import MWCAccountsAPI
from making_with_code_cli.curriculum import get_curriculum
from making_with_code_cli.styles import info

class StudentRepos:
    """An interface to students' repos. 
    Subsets of repos can be selected and iterated over.
    """

    def __init__(self, settings, max_threads=8):
        self.settings = settings
        self.max_threads = max_threads

    def apply(self, function, group=None, course=None, user=None, 
            unit=None, module=None, status_message=""):
        """Applies function to repo paths matching args, and returns the result.
        The function should take (sem, result, g, user, path, token).
        Application is in parallel, using up to max_threads.
        """
        sem = Semaphore(self.max_threads)
        results = []
        threads = []
        for g, user, path, token in self.iter_repos(group, course, user, unit, module):
            thread = Thread(target=function, args=(sem, results, g, user, path, token))
            thread.start()
            threads.append(thread)
        for i, thread in enumerate(threads):
            thread.join()
            print(end="\r" + info(f"{status_message}: {i+1}/{len(threads)}"))
        print()
        return results

    def iter_repos(self, group=None, course=None, user=None, unit=None, module=None):
        root = Path(self.settings['teacher_work_dir']).resolve()
        api = MWCAccountsAPI()
        roster = api.get_roster(self.settings['mwc_accounts_token'])
        for g in roster['teacher_groups']:
            if group and (group not in g['group_name']) and (group not in g['group_slug']):
                continue
            if course and course not in g['course_name']:
                continue
            curriculum = get_curriculum(g['curriculum_site_url'], g['course_name'])
            for username, token in g['student_tokens'].items():
                if user and user not in username:
                    continue
                for u in curriculum['units']:
                    if unit and (unit not in u['name']) and (unit not in u['slug']):
                        continue
                    for m in u['modules']: 
                        if module and (module not in m['name']) and (module not in m['slug']):
                            continue
                        path = root / g['group_slug'] / username / u['slug'] / m['slug']
                        yield g, username, path, token

