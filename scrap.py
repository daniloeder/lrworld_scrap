from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time, re

# EBAY LOGIN CREDENTIALS
USER_EMAIL = ''
USER_PASSWORD = ''

def get_categories():
    categories = []
    actions = ActionChains(driver)
    menu = driver.find_element(By.ID, 'dl-menu')
    menu_items = menu.find_elements(By.CLASS_NAME, 'has-submenu')
    items_categories = [item for item in menu_items]
    for category in items_categories:
        category_name = category.text
        while category_name == category.text:
            actions.move_to_element(category).perform()
            time.sleep(0.1)
        items_sub_categories = driver.find_elements(By.CLASS_NAME, 'nav-content')
        sub_category = []
        for item_sub_category in items_sub_categories:
            if item_sub_category.text:
                items_classes = item_sub_category.find_elements(By.TAG_NAME, 'li')
                classes = []
                for class_item in items_classes:
                    item_url = class_item.find_element(By.TAG_NAME, 'a').get_attribute('href')
                    #current_html = class_item.get_attribute('innerHTML')
                    #new_link = '''<a href="@scrap" style="display: inline-block; padding: 3px 3px; background-color: blue; color: white; text-align: center; font-size: 12px; text-decoration: none; border-radius: 3px; font-weight: bold;">Scrap</a>'''
                    #driver.execute_script("arguments[0].innerHTML = arguments[1];", class_item, current_html + new_link)
                    classes.append({
                        'name': class_item.text,
                        'url': item_url
                    })
                sub_category.append({
                    'name': item_sub_category.find_element(By.TAG_NAME, 'h4').text,
                    'classes': classes
                })
        categories.append({
            'name': category_name,
            'sub_categories': sub_category
        })
    actions.move_to_element(driver.find_element(By.CLASS_NAME, 'user-status-logged-out')).perform()
    for category in items_categories:
        a = category.find_element(By.TAG_NAME, 'a')
        current_html = category.get_attribute('innerHTML')
        new_button_html = '''
        <a id="scrapNowButton" href="''' + a.get_attribute('href') + '''?@scrapAll" style="display: inline-block; padding: 3px 3px; background-color: blue; color: white; text-align: center; font-size: 12px; text-decoration: none; border-radius: 3px; font-weight: bold;">Scrap</a>
        <script>
            document.getElementById('scrapNowButton').addEventListener('click', function() {
                document.title = 'scraped';
            });
        </script>
        '''
        # Append the new button to the existing HTML
        driver.execute_script("arguments[0].innerHTML = arguments[1];", category, current_html + new_button_html)
    time.sleep(1)
    return menu.get_attribute('innerHTML'), categories

js = ['summary__photos', 'summary__title', 'summary__category', 'summary__attributes--container', 'https://www.ebay.ch/sl/prelist/suggest?sr=cubstart', 'items-total']
def add_lr_world_button():
    button_script = """
        if (!document.getElementById('goToLRWorldButton')) {
            // Create button
            var button = document.createElement('button');
            button.id = 'goToLRWorldButton';
            button.innerHTML = 'Go to LR World';
            
            // Button styling
            button.style.position = 'fixed';
            button.style.right = '5%';
            button.style.top = '60%';  // Positioned below the eBay button
            button.style.transform = 'translateY(-50%)';  // Centers vertically
            button.style.backgroundColor = '#28a745';  // Green for LR World
            button.style.color = '#fff';  // White text
            button.style.fontSize = '20px';
            button.style.padding = '15px 30px';
            button.style.borderRadius = '8px';  // Rounded corners
            button.style.border = 'none';
            button.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';  // Soft shadow
            button.style.cursor = 'pointer';
            button.style.transition = 'all 0.3s ease';  // Smooth hover effect

            // Hover effect
            button.onmouseover = function() {
                button.style.backgroundColor = '#218838';  // Darker green on hover
            };
            button.onmouseout = function() {
                button.style.backgroundColor = '#28a745';  // Original green on hover out
            };

            // Append button to the document body
            document.body.appendChild(button);

            // Button click behavior
            button.addEventListener('click', function() {
                // Redirect to the specified URL
                window.location.href = 'https://shop.lrworld.com/home/ch/de?PHP=kEVOq3BtkLDyv91WMUw1Ag%3D%3D&casrnc=e2aaf';
            });
        }
    """
    driver.execute_script(button_script)

def add_images(product):
    print('Adding images...')
    try:
        # ADD IMAGES
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, js[0])))
        driver.execute_script("arguments[0].scrollIntoView();window.scrollBy(0, -50);", driver.find_element(By.CLASS_NAME, 'summary__photos'))
        time.sleep(1)
        if len(driver.find_elements(By.CLASS_NAME, 'uploader-thumbnails__container-empty--importFromWeb')) == 0:
            driver.find_elements(By.CLASS_NAME, 'se-expand-button__button-text')[0].click()
            driver.find_element(By.NAME, 'photoUploadWebPref').click()
            driver.find_elements(By.CLASS_NAME, 'se-expand-button__button-text')[0].click()
        driver.find_element(By.CLASS_NAME, 'uploader-thumbnails__container-empty--importFromWeb').click()
        if len(driver.find_elements(By.CLASS_NAME, 'se-panel-container')) == 0:
            print('No se-panel-container found, skipping...')
            return
        driver.find_element(By.CLASS_NAME, 'se-panel-container').click()
        for index, image_url in enumerate(product['images']):
            if index > 0:
                driver.find_element(By.NAME, 'addAdditional').click()
            input_blocks = driver.find_elements(By.CLASS_NAME, 'url-row')
            input_blocks[index].find_element(By.TAG_NAME, 'input').send_keys(image_url)
        # done
        driver.find_element(By.CLASS_NAME, 'se-panel-container__header').find_element(By.TAG_NAME, 'button').click()
    except Exception as e:
        print(f"Error while adding images: {e}")

def add_title(product):
    # ADD TITLE
    print('Adding title...')
    try:
        driver.execute_script("arguments[0].scrollIntoView();window.scrollBy(0, -50);", driver.find_element(By.CLASS_NAME, 'summary__title'))
        time.sleep(1)
        title_block = driver.find_element(By.CLASS_NAME, js[1]).find_element(By.CLASS_NAME, 'smry--section')
        title_input = title_block.find_element(By.TAG_NAME, 'input')
        title_input.clear()
        title_input.send_keys(product['name'])
    except Exception as e:
        print(f"Error while adding title: {e}")

def add_category():
    print('Selecting category...')
    try:
        while len(driver.find_elements(By.CLASS_NAME, js[2])) < 1:
            time.sleep(1)
        driver.execute_script("arguments[0].scrollIntoView();window.scrollBy(0, -50);", driver.find_element(By.CLASS_NAME, 'summary__category'))
        time.sleep(1)
        category_block = driver.find_element(By.CLASS_NAME, 'summary__category')
        time.sleep(0.1)
        # categoryId
        if category_block.find_element(By.NAME, 'categoryId').text == "Sonstige":
            return
        while len(driver.find_elements(By.CLASS_NAME, 'lightbox-dialog__main')) == 0:
            try:
                category_block.find_element(By.TAG_NAME, 'button').click()
                time.sleep(1)
                break
            except:
                time.sleep(0.1)
        time.sleep(1)
        # category-picker
        category_picker = driver.find_element(By.CLASS_NAME, 'lightbox-dialog__main')
        while len(category_picker.find_elements(By.CLASS_NAME, 'textbox__control')) == 0:
            category_picker.find_element(By.NAME, 'primaryCategory').click()
            time.sleep(3)
        category_picker.find_element(By.CLASS_NAME, 'textbox__control').send_keys('Beauty & Gesundheit > Sonstige')
        for _ in range(50):
            if len(driver.find_elements(By.NAME, 'categoryId')) > 2:
                break
            time.sleep(0.1)
        for option in driver.find_elements(By.NAME, 'categoryId'):
            if option.get_attribute('value') == '1277':
                option.click()
                break
        for _ in range(10):
            try:
                driver.find_element(By.CLASS_NAME, 'se-panel-container__header-suffix').click()
                break
            except:
                pass
            time.sleep(0.5)
        while len(driver.find_elements(By.CLASS_NAME, 'lightbox-dialog__main')) > 0:
            time.sleep(0.2)
    except Exception as e:
        print(f"Error while adding category: {e}")

def add_specifics():
    # ITEM SPECIFICS
    print('Adding specifics...')
    try:
        driver.execute_script("arguments[0].scrollIntoView();window.scrollBy(0, -50);", driver.find_element(By.CLASS_NAME, 'summary__attributes--container'))
        time.sleep(1)
        specifics_block = driver.find_element(By.CLASS_NAME, js[3])
        required = specifics_block.find_elements(By.CLASS_NAME, 'summary__attributes--section-container')[0]
        required_fields = required.find_elements(By.CLASS_NAME, 'summary__attributes--fields')
        other = specifics_block.find_elements(By.CLASS_NAME, 'summary__attributes--section-container')[1]
        other_fields = other.find_elements(By.CLASS_NAME, 'summary__attributes--fields')
        for field in required_fields:
            if len(field.find_elements(By.NAME, 'attributes.Brand')) > 0:
                while True:
                    try:
                        driver.find_element(By.NAME, 'attributes.Brand').click()
                        time.sleep(0.1)
                        driver.find_element(By.NAME, 'search-box-attributesBrand').send_keys("LR World")
                        break
                    except:
                        time.sleep(0.1)
                options = field.find_elements(By.CLASS_NAME, 'se-filter-menu-button__add-custom-value')
                if len(options) > 0:
                    options[0].click()
        for field in other_fields:
            print(field.text)
            if len(field.find_elements(By.NAME, 'attributes.Country/Region of Manufacture')) > 0:
                while True:
                    try:
                        driver.find_element(By.NAME, 'attributes.Country/Region of Manufacture').click()
                        time.sleep(0.1)
                        driver.find_element(By.NAME, 'search-box-attributesCountryRegionofManufacture').send_keys("Germany")
                        # click name "searchedOptions-attributesCountryRegionofManufacture"
                        driver.find_element(By.NAME, 'searchedOptions-attributesCountryRegionofManufacture').click()
                        break
                    except:
                        time.sleep(0.1)
                options = field.find_elements(By.CLASS_NAME, 'se-filter-menu-button__add-custom-value')
                if len(options) > 0:
                    options[0].click()
    except Exception as e:
        print(f"Error while adding specifics: {e}")

def add_condition():
    # ADD CONDITION
    print('Selecting condition...')
    try:
        driver.execute_script("arguments[0].scrollIntoView();window.scrollBy(0, -50);", driver.find_element(By.CLASS_NAME, 'summary__condition'))
        time.sleep(1)
        condition_block = driver.find_element(By.CLASS_NAME, 'summary__condition')
        # get condition-recommendation-value btn
        options = condition_block.find_elements(By.CLASS_NAME, 'condition-recommendation-value')
        if len(options) > 0:
            options[0].click()
    except Exception as e:
        print(f"Error while adding condition: {e}")

def add_description(product):
    # ADD DESCRIPTION
    print('Adding description...')
    try:
        description_block = driver.find_element(By.CLASS_NAME, 'summary__description')
        driver.execute_script("arguments[0].scrollIntoView();window.scrollBy(0, -50);", description_block)
        time.sleep(0.5)
        if len(driver.find_elements(By.ID, 'se-rte-frame__summary')) > 0:
            iframe = driver.find_element(By.ID, 'se-rte-frame__summary')
            driver.switch_to.frame(iframe)
            # Locate the contenteditable div inside the iframe
            editor_div = driver.find_element(By.CSS_SELECTOR, 'div[contenteditable="true"]')
            # Set the HTML content directly using JavaScript
            driver.execute_script(f"arguments[0].innerHTML = `{product['description']}`;", editor_div)
            time.sleep(0.1)
            driver.find_element(By.TAG_NAME, 'body').click()
            time.sleep(0.1)
            driver.switch_to.default_content()
        else:
            print('No description editor found, skipping...')
    except Exception as e:
        print(f"Error while adding description: {e}")

def add_pricing(product):
    # ADD PRICING
    print('Setting price...')
    try:
        while len(driver.find_elements(By.CLASS_NAME, 'summary__price')) == 0:
            time.sleep(1)
        driver.execute_script("arguments[0].scrollIntoView();window.scrollBy(0, -50);", driver.find_element(By.CLASS_NAME, 'summary__price'))
        time.sleep(1)
        price_block = driver.find_element(By.CLASS_NAME, 'summary__price')
        # button
        for button in price_block.find_elements(By.TAG_NAME, 'button'):
            if button.text == 'Auktion':
                button.click()
                break
        if button.text != 'Sofort-Kaufen':
            # listbox__options
            for option in price_block.find_elements(By.CLASS_NAME, 'listbox__option'):
                if option.text == 'Sofort-Kaufen':
                    option.click()
                    break
        # get input with name 'price'
        while len(price_block.find_elements(By.NAME, 'price')) == 0:
            time.sleep(0.5)
        time.sleep(0.1)
        price_input = price_block.find_element(By.NAME, 'price')
        price_input.send_keys(str(product['price']))
        time.sleep(0.1)
        # add quantity
        while price_block.find_element(By.NAME, 'quantity').get_attribute('value'):
            price_block.find_element(By.NAME, 'quantity').send_keys('\b')
        time.sleep(0.1)
        price_block.find_element(By.NAME, 'quantity').send_keys('5')
        time.sleep(0.1)
        # disable best offer
        if len(price_block.find_elements(By.NAME, 'bestOfferEnabled')) > 0:
            price_block.find_element(By.NAME, 'bestOfferEnabled').click()
        time.sleep(0.1)
    except Exception as e:
        print(f"Error while adding pricing: {e}")

def add_shipping():
    # ADD SHIPPING
    print('Setting shipping...')
    try:
        driver.execute_script("arguments[0].scrollIntoView();window.scrollBy(0, -50);", driver.find_element(By.CLASS_NAME, 'summary__shipping'))
        time.sleep(1)
        shipping_block = driver.find_element(By.CLASS_NAME, 'summary__shipping')
        try:
            select_block = shipping_block.find_element(By.CLASS_NAME, 'summary__shipping--section')
            if len(select_block.find_elements(By.CLASS_NAME, 'se-field--fluid')) > 0:
                select = select_block.find_element(By.CLASS_NAME, 'se-field--fluid')
                select.click()
                time.sleep(0.1)
                options = select_block.find_elements(By.CLASS_NAME, 'listbox__option')
                options[1].click()
                time.sleep(0.1)
                select.click()
        except Exception as e:
            print("Error:", e)
            time.sleep(1)
        try:
            preferences_block = shipping_block.find_element(By.CLASS_NAME, 'shipping-settings-container')
            button = preferences_block.find_element(By.TAG_NAME, 'button')
            button.click()
        except Exception as e:
            print("Error:", e)
        to_write = ''
        try:
            handling_time_block = driver.find_element(By.CLASS_NAME, 'se-panel-container__body').find_element(By.TAG_NAME, 'div')
            for i in range(5):
                if len(handling_time_block.find_elements(By.TAG_NAME, 'button')) > 0:
                    break
                time.sleep(1)
            to_write = driver.find_element(By.CLASS_NAME, 'se-panel-container__body').get_attribute('outerHTML')
            button = handling_time_block.find_element(By.TAG_NAME, 'button')
            for _ in range(10):
                try:
                    button.click()
                    time.sleep(0.1)
                    options = handling_time_block.find_elements(By.CLASS_NAME, 'listbox__option')
                    time.sleep(1)
                    options[3].click()
                    break
                except:
                    pass
            button.click()
            driver.find_element(By.CLASS_NAME, 'textual-display').click()
            time.sleep(0.1)
        except Exception as e:
            print("Error", e)
        try:
            prefecences_settings = driver.find_element(By.CLASS_NAME, 'se-panel-container__body')
            country_input = prefecences_settings.find_element(By.NAME, 'itemLocationCountry')
            country_input.click()
            print("Ok, clicked")
            if True:
                time.sleep(0.1)
                while country_input.get_attribute('value'):
                    country_input.send_keys('\b')
                country_input.clear()
                time.sleep(0.1)
                country_input.send_keys('Germany')
                time.sleep(0.1)
                print("Ok, clicked 2")
                # combobox__option
                prefecences_settings.find_element(By.CLASS_NAME, 'combobox__option').click()
                # itemLocation
                if len(prefecences_settings.find_elements(By.NAME, 'itemLocation')) > 0:
                    location_input = prefecences_settings.find_element(By.NAME, 'itemLocation')
                    location_input.send_keys('d-59227')
                # itemLocationCityState
                location_city_state = prefecences_settings.find_element(By.NAME, 'itemLocationCityState')
                location_city_state.clear()
                location_city_state.send_keys('Ahlen')
                print("Ok, clicked 3")
                driver.find_element(By.CLASS_NAME, 'se-panel-container__header-suffix').find_element(By.TAG_NAME, 'button').click()
                time.sleep(1)
        except Exception as e:
            print("Error:", e)
        try:
            # name packageDepth
            print("Last click")
            driver.find_element(By.NAME, 'packageDepth').click()
        except Exception as e:
            print("Error:", e)
    except Exception as e:
        print(f"Error while adding shipping: {e}")

def save():
    print('Saving...')
    try:
        driver.execute_script("arguments[0].scrollIntoView();window.scrollBy(0, -50);", driver.find_element(By.CLASS_NAME, 'summary__cta'))
        time.sleep(1)
        save_block = driver.find_element(By.CLASS_NAME, 'summary__cta')
        button = save_block.find_element(By.TAG_NAME, 'button')
        button.click()
        for button in driver.find_elements(By.TAG_NAME, 'button'):
            if button.text == 'Fertig':
                button.click()
                time.sleep(1)
                break
    except Exception as e:
        print(f"Error while saving: {e}")

def check_captcha(driver):
    # captcha_form
    if len(driver.find_elements(By.ID, 'captcha_form')) > 0:
        return True
    return False

def ebay_login(driver, USER_EMAIL, USER_PASSWORD, check_=True):
    if check_:
        print('Logging in to eBay...')
    try:
        driver.get(f"https://ebay.{'ch' if check_ else 'com'}/")
        time.sleep(1)
        try:
            if 'signin.ebay.' not in driver.find_element(By.ID, 'gh-top').find_element(By.TAG_NAME, 'a').get_attribute('href') and 'captcha' not in driver.current_url:
                return True
        except:
            pass
        driver.get(f"https://signin.ebay.{'ch' if check_ else 'com'}/")
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'userid')))
        if not check_ and check_captcha(driver):
            return False
        if len(driver.find_elements(By.ID, 'userid')) > 0:
            if not USER_EMAIL:
                print("Missing eBay login email, fill it manually...\n\n")
                u = ''
                p = ''
                while 'signin.ebay.ch' in driver.current_url:
                    time.sleep(0.01)
                return True
            else:
                try:
                    driver.find_element(By.ID, 'userid').send_keys(USER_EMAIL)
                    driver.find_element(By.ID, 'signin-continue-btn').click()
                    time.sleep(3)
                except:
                    pass
        if not USER_PASSWORD:
            WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.ID, 'pass')))
        else:
            if not check_ and check_captcha(driver):
                return False
            driver.find_element(By.ID, 'pass').send_keys(USER_PASSWORD)
        if len(driver.find_elements(By.ID, 'sgnBt')) > 0:
            driver.find_element(By.ID, 'sgnBt').click()
            return True
    except Exception as e:
        print(f"Error while logging in to eBay: {e}")
        time.sleep(1)

def check_for_template_list():
    if len(driver.find_elements(By.CLASS_NAME, 'template-list__title')) > 0:
        return driver.find_elements(By.CLASS_NAME, 'template-list__title')
    return []

def list_products_in_ebay(products):
    driver.get(js[4])
    time.sleep(3)
    i = 1
    templates_list = check_for_template_list()
    if len(templates_list) == 0:
        print('No template found...')
        return []
    print("Templage found, listing products...")
    for product in products:
        print(f"{i}/{len(products)} Listing product: {product['name']}")
        driver.get('https://www.ebay.ch/sl/prelist/suggest?sr=cubstart')
        templates_list = check_for_template_list()
        time.sleep(1)
        if len(driver.find_elements(By.CLASS_NAME, 'template-list__list')) > 0:
            templates_list[0].click()
            time.sleep(1)
            add_category()
            time.sleep(2)
            add_images(product)
            time.sleep(2)
            add_title(product)
            time.sleep(2)
            add_specifics()
            time.sleep(2)
            add_description(product)
            time.sleep(2)
            add_pricing(product)
            time.sleep(2)
            save()
            print(f"Product {product['name']} listed!\n\n")
        else:
            print('No template-list__list found, skipping...')
        i += 1

def show_scraped_list(products):
    new_menu = '''
    <div style="position: fixed; top: 10%; left: 1%; width: 350px; max-height: 80vh; background-color: #f8f9fa; padding: 20px; border-radius: 10px; box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.1); font-family: Arial, sans-serif; overflow-y: auto;">
        <h2 style="text-align: center; color: #333; margin-bottom: 20px; font-size: 20px;">Product List</h2>
    '''
    i = 0
    for product in products:
        new_menu += f'''
        <div style="display: flex; align-items: center; margin-bottom: 15px; background-color: #ffffff; padding: 10px; border-radius: 8px; box-shadow: 0px 2px 6px rgba(0, 0, 0, 0.1);">
            <img src="{product['images'][0]}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px; margin-right: 15px;" alt="{product['name']}">
            <div style="flex-grow: 1;">
                <div style="font-weight: bold; font-size: 14px; color: #333;">{product['name']}</div>
                <div style="color: #555; font-size: 13px; margin-top: 5px;">{product['price']}</div>
            </div>
            <!--<a target="_self" href="{f"https://www.ebay.ch/sl/prelist/?lrworld_{i}"}" target="_blank" style="background-color: #007BFF; color: white; padding: 8px 12px; text-decoration: none; border-radius: 5px; font-size: 12px; font-weight: bold;">List on eBay</a>
            -->
        </div>
        '''
    new_menu += '</div>'
    # Removing the product menu from your webpage
    driver.execute_script("""
        var menu = document.querySelector('div[style*="position: fixed"]');
        if (menu) {
            menu.remove();
        }
    """)
    # Injecting the new product menu into your webpage by appending it
    driver.execute_script("""
        var div = document.createElement('div');
        div.style.position = 'fixed';
        div.style.top = '10%';
        div.style.left = '2%';
        div.innerHTML = arguments[0];
        document.body.appendChild(div);
    """, new_menu)

def scrap_products(products_to_scrap):
    products = []
    i = 1
    for product_scrap in products_to_scrap:
        print(f"{i}/{len(products_to_scrap)} Scraping product: {product_scrap['title']}")
        driver.get(product_scrap['url'])
        for _ in range(6):
            if len(driver.find_elements(By.CLASS_NAME, 'price')) > 0:
                break
            time.sleep(1)
        time.sleep(1)
        product = scrap_product()
        if product:
            product['category'] += ' ' + product_scrap['class']
            products.append(product)
        else:
            print('Error while scraping product:', product_scrap['title'])
        i += 1
    return products

def scrap_product():
    try:
        product = {
            'name': "",
            'description': "",
            'category': "",
            'brand': "None",
            'type': "None",
            'color': "None",
            'price': "",
            'images': [],
            'filled': False
        }
        images = driver.find_element(By.CLASS_NAME, 'product-image-wrapper').find_elements(By.CLASS_NAME, 'MagicThumb-swap')
        for image in images:
            product['images'].append(image.get_attribute('href'))
        main = driver.find_element(By.CLASS_NAME, 'product-description-name')
        product['name'] = main.find_element(By.TAG_NAME, 'h1').text
        extras = main.find_elements(By.TAG_NAME, 'p')
        if len(extras) > 0:
            if ': ' in extras[0].text:
                product['upc'] = extras[0].text.split(': ')[1]
                extras = extras[1:]
        weight = None
        mililiters = None
        if len(extras) > 0:
            if ' g ' in extras[0].text:
                weight = extras[0].text
                extras = extras[1:]
                product['weight'] = weight
            elif ' ml ' in extras[0].text:
                mililiters = extras[0].text
                extras = extras[1:]
                product['mililiters'] = mililiters
        product['description'] = ''
        if len(driver.find_elements(By.CLASS_NAME, 'product-description-list')) > 0:
            main_description = driver.find_element(By.CLASS_NAME, 'product-description-list')
            main_description_html = main_description.get_attribute('innerHTML')
            product['description'] = re.sub(r'\s+', ' ', main_description_html).strip()
        information = driver.find_element(By.ID, 'moreInformation')
        sections = driver.find_element(By.CLASS_NAME, 'title-wrapper').find_elements(By.TAG_NAME, 'div')
        description_html = ''
        for i, section in enumerate(sections):
            section.click()
            time.sleep(1)
            content = information.find_elements(By.TAG_NAME, 'section')[1]
            # Find the section with id="panel1"
            panel1_div = content.find_element(By.ID, section.find_element(By.TAG_NAME, 'a').get_attribute('href').split('#')[-1])
            # JavaScript to get the inner HTML of only h2 and p direct children
            script = """
            var panel = arguments[0];
            var result = '';
            var children = panel.children;
            for (var i = 0; i < children.length; i++) {
                var tag = children[i].tagName.toLowerCase();
                if (tag === 'h2' || tag === 'p') {
                    result += children[i].outerHTML;
                }
            }
            return result;
            """
            # Execute the script to get the desired content as HTML
            filtered_html = driver.execute_script(script, panel1_div) + '<br>'
            description_html += re.sub(r'\s+', ' ', filtered_html).strip()
        product['description'] = description_html
        # get price
        product['price'] = driver.find_element(By.CLASS_NAME, 'price').text
        # get all breadcrumb items
        breadcrumb_items = driver.find_element(By.CLASS_NAME, 'breadcrumb-nav').find_elements(By.TAG_NAME, 'li')
        # get category
        product['category'] = breadcrumb_items[3].text
        # get brand
        product['brand'] = breadcrumb_items[4].text
        product['filled'] = True
        driver.execute_script("document.title = 'done-scraping';")
        return product
    except Exception as e:
        pass
    return False

def check_for_scrap_all(categories):
    for page in ['nutrition.html', 'figur.html', 'pflege.html', '/duft/', 'lr_world.html', 'marken.html']:
        if page in driver.current_url:
            for category in categories:
                if page == category['name'].lower().replace(" ", "_")+".html" or (page == '/duft/' and category['name'] == 'Duft'):
                    return scrap_all_subcategories(category)

def get_subcategorie_products():
    list_items = []
    try:
        if len(driver.find_elements(By.CLASS_NAME, 'items-total')):
            items_total = driver.find_element(By.CLASS_NAME, 'items-total').text.split(' ')[-1]
            while len(driver.find_elements(By.TAG_NAME, 'article')) < int(items_total):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
            items = driver.find_elements(By.TAG_NAME, 'article')
            for item in items:
                content = item.find_element(By.CLASS_NAME, 'content')
                title = content.find_element(By.TAG_NAME, 'h3').text
                price = content.find_element(By.CLASS_NAME, 'price').text
                image = item.find_element(By.CLASS_NAME, 'image').find_element(By.TAG_NAME, 'img').get_attribute('src')
                url = item.find_element(By.CLASS_NAME, 'image').find_element(By.TAG_NAME, 'a').get_attribute('href')
                list_items.append({'title': title, 'price': price, 'image': image, 'url': url})
    except Exception as e:
        print(f"Error while scraping subcategory: {e}")
    return list_items

def scrap_all_subcategories(category):
    to_scrap = []
    for sub_category in category['sub_categories']:
        for class_item in sub_category['classes']:
            driver.get(class_item['url'])
            time.sleep(1)
            new_products = get_subcategorie_products()
            for product in new_products:
                product['class'] = class_item['name']
                to_scrap.append(product)
    return to_scrap

# Automatically download and use the correct version of ChromeDriver
options = webdriver.ChromeOptions()
options.add_argument("--enable-features=UseOzonePlatform")
options.add_argument("--ozone-platform=wayland")
options.add_argument("--log-level=1")
options.add_argument("--incognito")
options.add_argument("--guest")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)

# Navigate to the main page
#driver.get('https://shop.lrworld.com/home/ch/de?PHP=kEVOq3BtkLDyv91WMUw1Ag%3D%3D&casrnc=e2aaf')
driver.get('https://shop.lrworld.com/cms/CH/de/')

products = []
product = {
    'name': "",
    'description': "",
    'category': "",
    'brand': "None",
    'type': "None",
    'color': "None",
    'price': "",
    'images': [],
    'filled': False
}

categories = None
menu = None
previous_url = None
loged_in = False

# Main loop to handle navigation and scraping
while True:
    try:
        while not categories:
            print('Getting categories...')
            menu, categories = get_categories()
            print("Done!")
        url_data = driver.current_url.split('/')
        if len(products) > 0 and previous_url != driver.current_url and 'signin.ebay.ch' not in driver.current_url:
                show_scraped_list(products)
        if 'shop.lrworld.com' in url_data:
            if previous_url != driver.current_url:
                if menu and menu != driver.find_element(By.ID, 'dl-menu'):
                    driver.execute_script("arguments[0].innerHTML = arguments[1];", driver.find_element(By.ID, 'dl-menu'), menu)
                if '@scrapAll' in driver.current_url:
                    print("Scraping products list...")
                    products_to_scrap = check_for_scrap_all(categories)
                    if products_to_scrap:
                        print(f"Done!, Found {len(products_to_scrap)} products to scrap")
                        scraped_products = scrap_products(products_to_scrap)
                        products.extend(scraped_products)
                        if len(products) > 0:
                            while not loged_in:
                                loged_in = ebay_login(driver, USER_EMAIL, USER_PASSWORD)
                            list_products_in_ebay(products)
                            a = 0/0
                    else:
                        print("No products to scrap found!")
                previous_url = driver.current_url
            if 'product' in url_data:
                try:
                    if WebDriverWait(driver, 10).until(EC.title_is("start-scraping")):
                        product = scrap_product()
                        driver.get('https://www.ebay.ch/sl/prelist/suggest?sr=cubstart')
                except:
                    pass
            else:
                # Reset button if URL does not match the target page
                driver.execute_script("var button = document.getElementById('goToEbayButton'); if (button) button.remove();")
        elif 'www.ebay.ch' in url_data:
            if 'https://www.ebay.ch/sl/prelist/?lrworld' in driver.current_url:
                product = products[int(driver.current_url.split('lrworld_')[-1])]
                driver.get('https://www.ebay.ch/sl/prelist/suggest?sr=cubstart')
            else:
                if not product['filled']:
                    if 'drafts' in url_data:
                        time.sleep(1)
                    else:
                        driver.get('https://shop.lrworld.com/home/ch/de?PHP=kEVOq3BtkLDyv91WMUw1Ag%3D%3D&casrnc=e2aaf')
                else:
                    add_lr_world_button()
                    if 'mode=AddItem' in url_data[3]:
                        add_images(product)
                        time.sleep(2)
                        add_title(product)
                        time.sleep(2)
                        add_category()
                        time.sleep(2)
                        add_specifics(product)
                        time.sleep(2)
                        add_condition()
                        time.sleep(2)
                        add_description(product)
                        time.sleep(2)
                        add_pricing(product)
                        time.sleep(2)
                        save()
                        print("Done!")
                        while True:
                            if 'mode=AddItem' not in driver.current_url:
                                break
                            time.sleep(1)
                        product = {
                            'name': "",
                            'description': "",
                            'category': "",
                            'brand': "None",
                            'type': "None",
                            'color': "None",
                            'price': "",
                            'images': [],
                            'filled': False
                        }
        elif 'signin.ebay.ch' in url_data:
            time.sleep(1)
        else:
            driver.get('https://shop.lrworld.com/home/ch/de?PHP=kEVOq3BtkLDyv91WMUw1Ag%3D%3D&casrnc=e2aaf')
    except Exception as e:
        print(f"Error occurred: {e}")
        break
    time.sleep(1)

