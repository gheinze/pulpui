from dotenv import load_dotenv, dotenv_values
from flask import Flask, request
from flask import jsonify
from flask import render_template
from flask_cors import CORS
import json
import requests


load_dotenv('./.flaskenv')
config = dotenv_values('./.flaskenv')
pulp_url= config["PULP_URL"]


app = Flask(
        __name__,
        static_folder = "./frontend/dist/assets",
        template_folder = "./frontend/dist"
        )

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return render_template("index.html", title="pulp-ui")
    # CORS work around
    #if app.debug:
    #    return requests.get('http://localhost:5000/{}'.format(path)).text
    #return render_template("index.html")


def _add_publication_details(session, distributions):
    """ Distribution -> Publication -> Repository Version -> Repository
    Traverse the path from distribution to repository to understand the details of a distribution.
    """
    for distribution in distributions['results']:

        publication_url = pulp_url + distribution['publication']
        r = session.get(publication_url)
        publication_result = r.json()

        repository_version_url = pulp_url + publication_result['repository_version']
        r = session.get(repository_version_url)
        version_result = r.json()
        distribution['version_created'] = version_result['pulp_created']
        distribution['version_number'] = version_result['number']

        repository_url = pulp_url + version_result['repository']
        r = session.get(repository_url)
        repo_result = r.json()
        distribution['repository_name'] = repo_result['name']
        distribution['versions_href'] = repo_result['versions_href']
        latest_repo_version_href = repo_result['latest_version_href']
        latest_version = latest_repo_version_href.rsplit('/', 2)[-2]
        distribution['latest_version'] = latest_version


@app.route('/api/rpm/distributions')
def get_rpm_distributions():

    with requests.Session() as s:
        s.auth = (config["PULP_USR"], config["PULP_PWD"])

        distribution_url = pulp_url + '/pulp/api/v3/distributions/rpm/rpm/'
        r = s.get(distribution_url)
        result = r.json()

        # Result contains an array of distributions, each item having:
        #   base_url:    full url to the distribution content
        #   name:        name of the distribution
        #   publication: href of the publication associated with this distribution
        #   pulp_href:   href of the distribution

        _add_publication_details(s, result)

        return result


def _get_publications_for_version(session, version_href):


    url = pulp_url + "/pulp/api/v3/publications/rpm/rpm"
    params = { "repository_version": version_href, "ordering": "ordering=-pulp_created" }
    r = session.get(url, params=params)
    publications_result = r.json()

    publications= []
    for publication in publications_result["results"]:
        p = { "publication_href": publication["pulp_href"], "publication_created": publication["pulp_created"] }
        publications.append(p)
        
    return publications


@app.route('/api/rpm/publications')
def get_publications_for_rpm_repo():
    """ Retrieve all the verions associated with a repo.
    Then retrieve all the publications associated with each version.
    """

    # All the versions associated with the repo associated with the publication
    versions_href = request.args['versions_href']

    with requests.Session() as s:

        s.auth = (config["PULP_USR"], config["PULP_PWD"])

        url = pulp_url + versions_href
        params = { "ordering": "-repository_version" }
        r = s.get(url, params=params)
        versions_result = r.json()

        result = []

        for version in versions_result['results']:
            publications = _get_publications_for_version(s, version['pulp_href'])
            j = { "version_href": version['pulp_href']
                 ,"created": version['pulp_created']
                 ,"number": version['number']
                 ,"publications": publications
                 }
            result.append(j)

        return json.dumps(result)


if __name__ == '__main__':
    app.run()
