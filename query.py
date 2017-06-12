import csv
import time
from selenium import webdriver
import selenium.webdriver.common.by as By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support  import expected_conditions as EC

def parseWaterfallTable(table):
    for index, item in list(enumerate(table)):
        text = item.text
        if text == "200 OK":
            return index

def findUrlTtfb(browser,urlToScan,gtMetrix):
    results = urlToScan.split()
    browser.get(gtMetrix)
    browser.find_element_by_css_selector('.js-analyze-form-url').send_keys(urlToScan)
    browser.find_element_by_css_selector('div.analyze-form-button button').click()
    WebDriverWait(browser,100).until(
        EC.presence_of_element_located((By.By.CLASS_NAME, 'report-waterfall'))
    )
    pagedetails = browser.find_elements_by_css_selector('span.report-page-detail-value')
    pageLoadTime = float(pagedetails[0].text.replace('s',''))
    totalPageSize = pagedetails[1].text
    if 'KB' in totalPageSize:
        totalPageSize = float(totalPageSize.replace('KB',''))/1000
    else:
        totalPageSize = float(totalPageSize.replace('MB',''))
    pageLoadRequestCount = float(pagedetails[2].text)

    browser.find_element_by_xpath('//a[text()="Waterfall"]')

    browser.switch_to.frame(browser.find_element_by_class_name('report-waterfall'))
    browser.get(browser.current_url)
    print(browser.current_url)
    WebDriverWait(browser,100).until(
        EC.presence_of_element_located((By.By.CLASS_NAME, 'pageName'))
    )
    waterfallNetStatus = browser.find_elements_by_css_selector('.netStatusLabel')
    index = parseWaterfallTable(waterfallNetStatus)
    waterfallNetReceiving = browser.find_elements_by_css_selector('.netReceivingBar')[index].value_of_css_property('width').replace('px','')
    waterfallNetWaiting = browser.find_elements_by_css_selector('.netWaitingBar')[index].value_of_css_property('width').replace('px','')
    waterfallNetTimeLabel = browser.find_elements_by_css_selector('span.netTimeLabel')[index].text
    if 'ms' in waterfallNetTimeLabel:
        waterfallNetTimeLabel = float(waterfallNetTimeLabel.replace('ms', ''))
    else:
        waterfallNetTimeLabel = float(waterfallNetTimeLabel.replace('s',''))*1000

    ttfb = float(waterfallNetWaiting) / float(waterfallNetReceiving) * waterfallNetTimeLabel
    results.append(ttfb)
    results.append(pageLoadTime)
    results.append(totalPageSize)
    results.append(pageLoadRequestCount)
    return results

gtMetrix = "https://gtmetrix.com/"
browser = webdriver.PhantomJS()
currDay = time.strftime("%m/%d/%Y")


with open(r'\\nas\Sharecare\share\Web Analytics\Automated Reports\Page Speed Report\Pages to Test.csv') as pageInputList, open(r'//nas/Sharecare/share/Web Analytics/Automated Reports/Page Speed Report/Page Speed Output.csv','a',newline='') as pageOutputList:
    pages = csv.reader(pageInputList)
    resultsPage = csv.writer(pageOutputList)
    failedPages = list([])
    for row in pages:
        print(row[0])
        try:
            output = findUrlTtfb(browser,row[0],gtMetrix)
            output.insert(0,currDay)
            resultsPage.writerow(output)
            print(output)
        except:
            failedPages.append(row[0])
            print("Failed: " + row[0])

#for page in failedPages:
#   try:
#        output = findUrlTtfb(browser, page, gtMetrix)
#        output.insert(0,currDay)
#        resultsPage.writerow(output)
#        print(output)
#        time.sleep(10)
#    except:
#        print("Failed: " + row[0])

while len(failedPages) > 1:
    for i, page in enumerate(failedPages):
        try:
            output = findUrlTtfb(browser, page, gtMetrix)
            output.insert(0, currDay)
            resultsPage.writerow(output)
            print(output)
            del failedPages[i]
            time.sleep(20)
        except:
            print(page + ' failed. Retrying...')


