from playwright.sync_api import Page, expect


def create_entry(page: Page, base_url, title, description):
    page.goto(f'{base_url}/entries/new')
    page.fill('#title', title)
    page.fill('#description', description)
    page.click('button[type=submit]')


def test_empty_list_shows_empty_state(page: Page, base_url):
    page.goto(base_url)
    expect(page.locator('#empty-state')).to_be_visible()
    expect(page.get_by_role('link', name='Create entry')).to_be_visible()


def test_index_alias_lands_on_root(page: Page, base_url):
    page.goto(f'{base_url}/index')
    assert page.url.rstrip('/') == base_url


def test_create_success(page: Page, base_url):
    create_entry(page, base_url, 'Buy milk', 'Two litres')
    assert page.url.rstrip('/') == base_url
    expect(page.locator('.alert-success')).to_have_text('Entry created.')
    row = page.locator('tbody tr')
    expect(row).to_have_count(1)
    expect(row).to_contain_text('Buy milk')
    expect(row).to_contain_text('Not done')


def test_create_validation_failure_shows_inline_errors(page: Page, base_url):
    page.goto(f'{base_url}/entries/new')
    page.click('button[type=submit]')
    expect(page.locator('#title-error')).to_have_text('Title is required.')
    expect(page.locator('#description-error')).to_have_text('Description is required.')
    page.goto(base_url)
    expect(page.locator('#empty-state')).to_be_visible()


def test_create_too_long_title_shows_error_and_keeps_input(page: Page, base_url):
    create_entry(page, base_url, 'x' * 65, 'desc')
    expect(page.locator('#title-error')).to_have_text('Title must be 64 characters or fewer.')
    expect(page.locator('#description')).to_have_value('desc')


def test_edit_success(page: Page, base_url):
    create_entry(page, base_url, 'Old title', 'Old desc')
    page.get_by_role('link', name='Edit').click()
    expect(page.locator('#title')).to_have_value('Old title')
    page.fill('#title', 'New title')
    page.fill('#description', 'New desc')
    page.click('button[type=submit]')
    expect(page.locator('.alert-success')).to_have_text('Entry updated.')
    expect(page.locator('tbody tr')).to_contain_text('New title')
    expect(page.locator('tbody tr')).to_contain_text('New desc')


def test_edit_validation_failure(page: Page, base_url):
    create_entry(page, base_url, 'Keep', 'Keep desc')
    page.get_by_role('link', name='Edit').click()
    page.fill('#title', '   ')
    page.click('button[type=submit]')
    expect(page.locator('#title-error')).to_have_text('Title is required.')
    page.goto(base_url)
    expect(page.locator('tbody tr')).to_contain_text('Keep')


def test_toggle_status_persists_after_reload(page: Page, base_url):
    create_entry(page, base_url, 'Toggle me', 'desc')
    page.get_by_role('button', name='Turn Status').click()
    expect(page.locator('.alert-success')).to_have_text('Entry marked as done.')
    expect(page.locator('tbody tr .badge')).to_have_text('Done')
    page.reload()
    expect(page.locator('tbody tr .badge')).to_have_text('Done')
    page.get_by_role('button', name='Turn Status').click()
    expect(page.locator('tbody tr .badge')).to_have_text('Not done')


def test_delete_with_confirmation(page: Page, base_url):
    create_entry(page, base_url, 'Doomed', 'desc')
    page.get_by_role('link', name='Delete').click()
    expect(page.locator('#delete-title')).to_have_text('Doomed')
    page.get_by_role('button', name='Delete').click()
    expect(page.locator('.alert-success')).to_have_text('Entry deleted.')
    expect(page.locator('#empty-state')).to_be_visible()


def test_delete_cancel_keeps_entry(page: Page, base_url):
    create_entry(page, base_url, 'Survivor', 'desc')
    page.get_by_role('link', name='Delete').click()
    page.get_by_role('link', name='Cancel').click()
    expect(page.locator('tbody tr')).to_contain_text('Survivor')


def test_missing_entry_shows_custom_404(page: Page, base_url):
    response = page.goto(f'{base_url}/entries/999999/edit')
    assert response.status == 404
    expect(page.locator('h1')).to_have_text('404')
