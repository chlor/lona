from playwright.async_api import async_playwright

from lona.html import Select, Option
from lona.pytest import eventually
from lona import LonaView

GET_OPTIONS = 'e => Array.from(e.selectedOptions).map(option => option.value)'


async def test_selects(lona_app_context):
    """
    This test tests HTML selects and multi selects, with and without pre
    selections, using a browser.
    """

    test_data = {}

    def setup_app(app):

        # select ##############################################################
        @app.route('/select/nothing-selected/')
        class NothingSelected(LonaView):
            def handle_request(self, request):
                select = Select(
                    Option('Foo', value='foo'),
                    Option('Bar', value='bar'),
                    Option('Baz', value='baz'),
                    bubble_up=True,
                )

                test_data['select/nothing-selected'] = select.value

                self.show(select)

                self.await_change(select)
                test_data['select/nothing-selected'] = select.value

        @app.route('/select/pre-selected/')
        class PreSelected(LonaView):
            def handle_request(self, request):
                select = Select(
                    Option('Foo', value='foo'),
                    Option('Bar', value='bar', selected=True),
                    Option('Baz', value='baz'),
                    bubble_up=True,
                )

                test_data['select/pre-selected'] = select.value

                self.show(select)

                self.await_change(select)
                test_data['select/pre-selected'] = select.value

        # multi select ########################################################
        @app.route('/multi-select/nothing-selected/')
        class MultiSelectNothingSelected(LonaView):
            def handle_request(self, request):
                select = Select(
                    Option('Foo', value='foo'),
                    Option('Bar', value='bar'),
                    Option('Baz', value='baz'),
                    multiple=True,
                    bubble_up=True,
                )

                test_data['multi-select/nothing-selected'] = select.value

                self.show(select)

                self.await_change(select)
                test_data['multi-select/nothing-selected'] = select.value

        @app.route('/multi-select/pre-selected/')
        class MultiSelectPreSelected(LonaView):
            def handle_request(self, request):
                select = Select(
                    Option('Foo', value='foo', selected=True),
                    Option('Bar', value='bar', selected=True),
                    Option('Baz', value='baz'),
                    multiple=True,
                    bubble_up=True,
                )

                test_data['multi-select/pre-selected'] = select.value

                self.show(select)

                self.await_change(select)
                test_data['multi-select/pre-selected'] = select.value

    context = await lona_app_context(setup_app)

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        browser_context = await browser.new_context()
        page = await browser_context.new_page()

        # select / nothing selected ###########################################
        # initial value
        await page.goto(context.make_url('/select/nothing-selected/'))
        await page.wait_for_selector('select')

        selected_options = await page.eval_on_selector('select', GET_OPTIONS)

        assert selected_options == ['foo']

        for attempt in eventually():
            async with attempt:
                assert test_data['select/nothing-selected'] == 'foo'

        # user select
        await page.select_option('select', 'bar')

        selected_options = await page.eval_on_selector('select', GET_OPTIONS)

        assert selected_options == ['bar']

        for attempt in eventually():
            async with attempt:
                assert test_data['select/nothing-selected'] == 'bar'

        # select / pre selected ###############################################
        # initial value
        await page.goto(context.make_url('/select/pre-selected/'))
        await page.wait_for_selector('select')

        selected_options = await page.eval_on_selector('select', GET_OPTIONS)

        assert selected_options == ['bar']

        for attempt in eventually():
            async with attempt:
                assert test_data['select/pre-selected'] == 'bar'

        # user select
        await page.select_option('select', 'foo')

        selected_options = await page.eval_on_selector('select', GET_OPTIONS)

        assert selected_options == ['foo']

        for attempt in eventually():
            async with attempt:
                assert test_data['select/pre-selected'] == 'foo'

        # multi / nothing selected ############################################
        # initial value
        await page.goto(context.make_url('/multi-select/nothing-selected/'))
        await page.wait_for_selector('select')

        selected_options = await page.eval_on_selector('select', GET_OPTIONS)

        assert selected_options == []

        for attempt in eventually():
            async with attempt:
                assert test_data['multi-select/nothing-selected'] == ()

        # user select
        await page.select_option('select', ['foo', 'bar'])

        selected_options = await page.eval_on_selector('select', GET_OPTIONS)

        assert selected_options == ['foo', 'bar']

        for attempt in eventually():
            async with attempt:
                assert test_data['multi-select/nothing-selected'] == (
                    'foo',
                    'bar',
                )

        # multi / pre selected ################################################
        # initial value
        await page.goto(context.make_url('/multi-select/pre-selected/'))
        await page.wait_for_selector('select')

        selected_options = await page.eval_on_selector('select', GET_OPTIONS)

        assert selected_options == ['foo', 'bar']

        for attempt in eventually():
            async with attempt:
                assert test_data['multi-select/pre-selected'] == ('foo', 'bar')

        # user select
        await page.select_option('select', ['foo', 'baz'])

        selected_options = await page.eval_on_selector('select', GET_OPTIONS)

        assert selected_options == ['foo', 'baz']

        for attempt in eventually():
            async with attempt:
                assert test_data['multi-select/pre-selected'] == (
                    'foo',
                    'baz',
                )

        # user deselect
        await page.goto(context.make_url('/multi-select/pre-selected/'))
        await page.wait_for_selector('select')
        await page.select_option('select', [])

        selected_options = await page.eval_on_selector('select', GET_OPTIONS)

        assert selected_options == []

        for attempt in eventually():
            async with attempt:
                assert test_data['multi-select/pre-selected'] == ()
