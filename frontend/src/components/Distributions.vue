<script setup>
import { ref, computed, onMounted } from "vue";
import axios from "axios";
import pulpService from "@/services/pulpService";

import DataTable from "primevue/datatable";
import Button from "primevue/button";
import Column from "primevue/column";
import ColumnGroup from "primevue/columngroup"; //optional for column grouping
import Toolbar from 'primevue/toolbar';
import OverlayPanel from 'primevue/overlaypanel';
import Textarea from 'primevue/textarea';

import { useSelectPublication } from '@/components/selectPublication.js';


const { presentPublication, publications, isPublicationLoading, modDistCmd, versionSelected  }  = useSelectPublication();
const publicationOverlay = ref();

const distributions = ref(null);
const isLoading = ref(false);
const selectedDistribution = ref(null);

const synchOverlay = ref();
const synchCmd = ref(null);


function loadDistributions() {

  distributions.value = null;
  isLoading.value = true;

  pulpService.getRpmDistributions()

    .then((response) => {

      response.data.results.forEach((result) => {
        result.version_created = result.version_created
          .substring(0, 16)
          .replace("T", " ");
          //.replace(/(....)(..)(..)/, "$1-$2-$3");
      });

      distributions.value = response.data.results;
      isLoading.value = false;
    })

    .catch((error) => {
      console.log(error);
      isLoading.value = false;
    });

}


function openUrl(url) {
  window.open(url);
}


function presentSync(event, repository_name) {
  synchCmd.value = `
# Sync a repository (implicitly versioning it)
pulp rpm repository  sync   --name       ${repository_name}

# Create a publication based on the latest repository version
pulp rpm publication create --repository ${repository_name}
`
  synchOverlay.value.toggle(event);
}


function copyToClipboard(txt) {
  navigator.clipboard.writeText(txt);
}


onMounted(() => {
  loadDistributions();
})

</script>

<template>
  <div>

      <Toolbar>
        <template #end>
          <Button class="mr-2" @click="loadDistributions" :loading="isLoading">Discover</Button>
        </template>
      </Toolbar>
      
      <div class="distribution-margin">
        <DataTable :value="distributions" :loading="isLoading" class="p-datatable-sm">
        
          <template #empty>
            <div class="centered">No data</div>
          </template>

          <template #loading>
            <h4>Loading records, please wait...</h4>
          </template>

          <template #header>
            <h4>RPM Distributions</h4>
          </template>

          <Column>
            <template #body="{data}">
              <Button @click="openUrl(data.base_url)" icon="pi pi-external-link" class="p-button-rounded p-button-secondary p-button-text"  v-tooltip="data.base_url"/>
            </template>
          </Column>

          <Column field="name"     header="Distribution" bodyStyle="text-align: left"></Column>
          <Column field="repository_name" header="Repository" bodyStyle="text-align: left"></Column>

          <Column header="Synch" >
            <template #body="{data}">
              <Button @click="presentSync($event, data.repository_name)" icon="pi pi-sync" class="p-button-rounded p-button-secondary p-button-text" v-tooltip="'Create new version'"/>
            </template>
          </Column>

          <Column field="latest_version"  header="Latest Ver"    bodyStyle="text-align: left"></Column>

          <Column header="Promote" >
            <template #body="{data}">
              <Button @click="presentPublication($event, data.name, data.versions_href, publicationOverlay)" icon="pi pi-arrow-up-right" class="p-button-rounded p-button-secondary p-button-text"  v-tooltip="'Choose another version'"
                  :disabled="data.latest_version == data.version_number"
              />
            </template>
          </Column>

          <Column field="version_number"  header="Current Ver"    bodyStyle="text-align: left"></Column>
          <Column field="version_created" header="Current Ver Synch" bodyStyle="text-align: left"></Column>

        </DataTable>
      </div>


      <OverlayPanel ref="synchOverlay" :showCloseIcon="true">
        <h4>CLI commands to synch a repository (creating a new version) and create a new publication</h4>
        <div><Button @click="copyToClipboard(synchCmd)" icon="pi pi-copy" class="p-button-rounded p-button-secondary p-button-text"  v-tooltip="'Copy'"/></div>
        <Textarea v-model="synchCmd" :autoResize="true" rows="5" cols="100" />
      </OverlayPanel>


      <OverlayPanel ref="publicationOverlay" :showCloseIcon="true" id="overlay_panel" style="width: 800px" aria:haspopup="true" aria-controls="overlay_panel">
        <DataTable :value="publications" :selectionMode="'single'" @row-click="versionSelected($event)"  dataKey="number" :loading="isPublicationLoading">
          <template #header>
            <div v-if="modDistCmd" >
              <h4>CLI command to point publication to selected distribution</h4>
              <div><Button @click="copyToClipboard(modDistCmd)" icon="pi pi-copy" class="p-button-rounded p-button-secondary p-button-text"  v-tooltip="'Copy'"/></div>
              <Textarea v-model="modDistCmd" :autoResize="true" rows="5" cols="70" />
            </div>
            <h4>Select a Publication</h4>
          </template>

          <Column field="number"  header="Version" bodyStyle="text-align: left"></Column>
          <Column field="created" header="Created" bodyStyle="text-align: left"></Column>
        </DataTable>
      </OverlayPanel>

  </div>
</template>

<style scoped>
a {
  color: #42b983;
}

.centered {
  text-align: center;
}

.right {
  margin-left: auto; 
  margin-right: 0;
}

.distribution-margin {
  margin-top: 20px;
  margin-bottom: 20px;
  margin-right: 20px;
  margin-left: 20px;
}

</style>
