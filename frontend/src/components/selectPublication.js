import { ref, unref } from "vue";
import pulpService from "@/services/pulpService";


// Factoring out the functions used by the "Promotion" button
// which shows a selectable Overlay of publications that could
// be associated with the distribution.

export function useSelectPublication() {

    const isPublicationLoading = ref(false);
    const selectedDistribution = ref(null);
    const publications = ref(null);
    const modDistCmd = ref(null);


    function presentPublication(event, distribution_name, versions_href, publicationOverlay) {

        // Listing the versions rather than the publications
        // In actuality, each version could be associated with multiple publications

        selectedDistribution.value = distribution_name;
        modDistCmd.value = null;
        publications.value = null;
        isPublicationLoading.value = true;

        pulpService.getRpmPublications(versions_href)

            .then((response) => {

            response.data.forEach((version) => {
                version.created = version.created
                .substring(0, 16)
                .replace("T", " ");
            });

            publications.value = response.data;
            isPublicationLoading.value = false;

            })

            .catch((error) => {
            isPublicationLoading.value = false;
            console.log(error);
            });
        
        unref(publicationOverlay).toggle(event);

    }


    function versionSelected(e) {

        // A version may have multiple publications associated. Select first one
        let publications = e.data.publications;

        if (Array.isArray(publications) && publications.length) {
            modDistCmd.value = "pulp rpm distribution update --name " + selectedDistribution.value + 
            " --publication $BASE_ADDR" + publications[0].publication_href;
        } else {
            modDistCmd.value = "No distribution for this version";
        }

    }


    return { presentPublication, publications, isPublicationLoading, modDistCmd, versionSelected };

}
