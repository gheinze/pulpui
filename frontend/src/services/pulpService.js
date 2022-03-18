import axios from 'axios';
import { PULP_UI_SERVICE_URL } from '@/config.js';


class PulpService {

    getRpmDistributions() {
        let service_url = PULP_UI_SERVICE_URL + 'rpm/distributions';
        return axios.get(service_url);
    }

    getRpmPublications(versions_href) {
        let service_url = PULP_UI_SERVICE_URL + 'rpm/publications';
        const params = new URLSearchParams([['versions_href', versions_href]]);
        return axios.get(service_url, { params });
    }


}

export default new PulpService();
