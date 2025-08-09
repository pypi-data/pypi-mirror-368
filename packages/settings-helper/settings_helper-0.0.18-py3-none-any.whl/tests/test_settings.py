import settings_helper as sh


get_setting = sh.settings_getter('settings_helper')
get_setting_num_strings = sh.settings_getter('settings_helper', keep_num_as_string=True)
get_setting_default = sh.settings_getter('settings_helper', 'default')
get_setting_dev = sh.settings_getter('settings_helper', 'dev')
get_setting_test = sh.settings_getter('settings_helper', 'test')


class TestEnv:
    def test_app_env_is_test(self):
        assert sh.APP_ENV == 'test'

    def test_settings_getter_uses_test_section(self):
        assert get_setting_test('redis_url') != get_setting_default('redis_url')
        assert get_setting_test('redis_url') != get_setting_dev('redis_url')
        assert get_setting_test('redis_url') == get_setting('redis_url')


class TestGetting:
    def test_get_number(self):
        value = get_setting('something')
        assert type(value) == int
        assert value == 100
        value = get_setting('something_else')
        assert type(value) == float
        assert value == 2.0

    def test_get_number_as_strings(self):
        value = get_setting_num_strings('something')
        assert type(value) == str
        assert value == '100'
        value = get_setting_num_strings('something_else')
        assert type(value) == str
        assert value == '2.0'

    def test_get_string(self):
        value = get_setting('redis_url')
        assert type(value) == str

    def test_get_nonexistant(self):
        value = get_setting('should_not_be_anything')
        assert value == ''
        value = get_setting('should_not_be_anything', 10)
        assert value == 10

    def test_get_list(self):
        value = get_setting('things')
        assert type(value) == list
        assert value[0] == None
        assert type(value[1]) == bool
        assert type(value[2]) == bool
        assert type(value[3]) == int
        assert type(value[4]) == float
        assert type(value[5]) == str

    def test_get_list_number_as_strings(self):
        value = get_setting_num_strings('things')
        assert type(value) == list
        assert value[0] == None
        assert type(value[1]) == bool
        assert type(value[2]) == bool
        assert type(value[3]) == str
        assert type(value[4]) == str
        assert type(value[5]) == str

    def test_inherited_setting(self):
        assert get_setting_default('something') == get_setting('something')
        assert get_setting_default('something') != get_setting_dev('something')

    def test_all_settings(self):
        settings = sh.get_all_settings('settings_helper')
        assert settings['test']['things'] == [None, True, False, 1, 2.5, 'dogs']
        assert settings['test']['redis_url'] != settings['dev']['redis_url']
        assert settings['test']['redis_url'] == get_setting('redis_url')
        assert 'something' in settings['dev']
        assert 'something' in settings['test']
        assert 'something_else' not in settings['dev']
        assert 'something_else' in settings['test']
        assert settings['test']['something_else'] == 2.0

    def test_all_settings_number_as_strings(self):
        settings = sh.get_all_settings('settings_helper', keep_num_as_string=True)
        assert settings['test']['things'] == [None, True, False, '1', '2.5', 'dogs']
        assert settings['test']['something_else'] == '2.0'
