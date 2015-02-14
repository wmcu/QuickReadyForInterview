from flask import Flask, jsonify, render_template, request, redirect, session, url_for
import requests
import nytime
import xml.etree.ElementTree as ET
from hashlib import sha1
from random import random


# Create an Flask app object.  We'll use this to create the routes.
app = Flask(__name__)

# Allow Flask to autoreload when we make changes to `app.py`.
app.config['DEBUG'] = True
access_token = ""

# web_url = r'https://quick-ready-for-interview.herokuapp.com'
web_url = r'http://localhost:5000'


# Three main pages
@app.route('/')
def index():
    return render_template('login.html')


@app.route('/search', methods=["GET", "POST"])
def search():
    return render_template('search.html')


@app.route('/results', methods=["GET", "POST"])
def results():
    data = {}
    if request.method == "POST":
        keyword = request.form['company-name']
        data['glassdoor'] = glassdoor(keyword)
        data['linkedin'] = goCompany(keyword)
        data['nytimes'] = nytimes(keyword)
        data['facebook'] = facebook(keyword)
        return render_template('results.html', api_data=data)
    else:
        return render_template('search.html')


# Login related pages
@app.route('/login')
def login():
    api_key = '78hfrhpe6d2v7h'
    random_state = sha1('%s' % random()).hexdigest()[:16]
    callback_url = r'%s/linkedin' % web_url
    payload = {
        'response_type': 'code',
        'client_id': api_key,
        'scope': 'r_fullprofile r_emailaddress r_network',
        'state': random_state,
        'redirect_uri': callback_url
    }
    base_url = "https://www.linkedin.com/uas/oauth2/authorization"
    response = requests.get(base_url, params=payload)
    return redirect(response.url)


@app.route('/linkedin')
def getToke():
    authenticationCode = request.args['code']
    global access_token
    base_url = "https://www.linkedin.com/uas/oauth2/accessToken"
    callback_url = r'%s/linkedin' % web_url
    para = {
        'grant_type': 'authorization_code',
        'code': authenticationCode,
        'redirect_uri': callback_url,
        'client_id': '78hfrhpe6d2v7h',
        'client_secret': 'mLT3bcX7i4xYZYeU'
    }
    response = requests.post(base_url, params=para)
    response_dict = response.json()
    access_token = response_dict['access_token']
    print access_token
    print url_for('static', filename='style.css')
    return redirect(url_for('search'))


# Error Handler
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(error):
    return render_template('500.html'), 500


@app.route('/info/<company_name>')
def get_posts(company_name):
    #Returns the list of updates of a company.
    TOKEN ='575731909230644|ZuJwTeYLANGBOsZFWPczcx8JDZo'
    parameters = {'access_token': TOKEN}
    response = requests.get('https://graph.facebook.com/'+ company_name + '/feed', params=parameters)
    response_dict = response.json()
    return jsonify(response_dict)

# # for testing glassdoor search
# @app.route('/glassdoor/<search_query>')
# def search_glassdoor(search_query):
#     user_agent = {'User-agent': request.headers.get('User-Agent')}
#     glassdoor_url = "http://api.glassdoor.com/api/api.htm?v=1&format=json&t.p=29781&t.k=jQdxv7dRxPc&action=employers&userip=0.0.0.0&useragent=Chrome&q=" + search_query
#     glassdoor_response_dict = requests.get(glassdoor_url, headers = user_agent).json()
#     glassdoor_response_dict = process_glassdoor_response(glassdoor_response_dict, search_query)
#     return jsonify(glassdoor_response_dict)

def process_glassdoor_response(api_dict, company_name):
    filtered_dict = {"companies":[]}
    if api_dict.get("success") is False:
        return filtered_dict
    response_dict = api_dict.get("response")
    if not response_dict:
        return filtered_dict
    employers_list = response_dict.get("employers")
    if not employers_list:
        return filtered_dict
    for employer in employers_list:
        if company_name.lower() in employer.get("name").lower():
            filtered_employer = {"name":employer.get("name"),"website":employer.get("website"),
                                 "industry":employer.get("industry"),"logo":employer.get("squareLogo"),"number_of_ratings":employer.get("numberOfRatings"),
                                 "overall_rating":employer.get("overallRating"),"rating_description":employer.get("ratingDescription"),
                                 "culture_and_values_rating":employer.get("cultureAndValuesRating"),
                                 "senior_leadership_rating":employer.get("seniorLeadershipRating"),
                                 "compensation_and_benefits_rating":employer.get("compensationAndBenefitsRating"),
                                 "career_opportunities_rating":employer.get("careerOpportunitiesRating"),
                                 "work_life_balance_rating":employer.get("workLifeBalanceRating"),
                                 "recommend_to_friend_rating":employer.get("recommendToFriendRating")}
            if employer.get("ceo"):
                filtered_employer["ceo"] = employer.get("ceo")
            filtered_dict["companies"].append(filtered_employer)
            return filtered_dict
    return filtered_dict


# Backend API
def glassdoor(keyword):
    user_agent = {'User-agent': request.headers.get('User-Agent')}
    glassdoor_url = "http://api.glassdoor.com/api/api.htm?v=1&format=json&t.p=29781&t.k=jQdxv7dRxPc&action=employers&userip=0.0.0.0&useragent=Chrome&q=" + keyword
    glassdoor_response_dict = requests.get(glassdoor_url, headers = user_agent).json()
    glassdoor_response_dict = process_glassdoor_response(glassdoor_response_dict, keyword)
    return glassdoor_response_dict


@app.route('/searchCompany/<company_name>')
def goCompany(company_name):
    global access_token
    companyName =None
    companyDescription=None
    authenticatedGetUrl = "https://api.linkedin.com/v1/company-search"
    print "----------------------------->"
    print access_token
    passin = {
        'oauth2_access_token': access_token,
        'keywords': company_name
    }
    response2 = requests.get(authenticatedGetUrl, params=passin)
    root = ET.fromstring(response2.text.encode('ascii', 'ignore'))
    if root is None:
        print "root is none"
    companiesTag = root.find('companies')
    if companiesTag is None:
        print "companies is none"
    else:
        companyTag = companiesTag.find('company')
        if companyTag is None:
            print "companyTag is none"
        else:
            companyID = companyTag.find('id').text
            companySearchByID = "https://api.linkedin.com/v1/companies/" + companyID
            companySearchByID = companySearchByID + ":(name,description)"
            passin3 = {'oauth2_access_token': access_token}

            response3 = requests.get(companySearchByID, params=passin3)
            root = ET.fromstring(response3.text.encode('ascii', 'ignore'))

            companyName = root.find('name').text
            companyDescription = root.find('description').text

    jsonOutput = {'name': companyName, 'description': companyDescription}
    return jsonOutput


def facebook(keyword):
    # Returns the list of updates of a company.
    TOKEN = '575731909230644|ZuJwTeYLANGBOsZFWPczcx8JDZo'
    parameters = {'access_token': TOKEN}
    response = requests.get('https://graph.facebook.com/' + keyword + '/feed', params=parameters)
    response_dict = response.json()
    info_collection = []
    ret = {'data': info_collection}
    if 'error' in response_dict:
        return ret
    for item in response_dict['data']:
        abstract = {}
        if ('status_type' in item and 'name' in item and 'message' in item and item['status_type'] == "shared_story"):
            abstract['link'] = item['link']
            abstract['message'] = item['message']
            abstract['name'] = item['name']
            abstract['picture'] = item['picture']
            abstract['pub_date'] = item['updated_time'][:10]
            info_collection.append(abstract)
    return ret


def nytimes(keyword):
    result = nytime.nytime_json(keyword)
    return result

# If the user executed this python file (typed `python app.py` in their
# terminal), run our app.
if __name__ == '__main__':
    app.run(host='0.0.0.0')
