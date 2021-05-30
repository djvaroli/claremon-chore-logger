<template>
  <section class="vertical-form">
    <b-field label="Filter by">
      <b-autocomplete
          placeholder="How to search"
          :open-on-focus="true"
          field="fieldDisplayName"
          :data="validFields"
          @select="option => (filterField = option.fieldName)"
          :clearable=true
      >
      </b-autocomplete>
    </b-field>
    <b-field label="Name">
      <b-autocomplete
        placeholder="What to search for"
        :open-on-focus="true"
        field="value"
        :data="values"
        @select="option => (filterTerm = option.value)"
        :clearable=true
        >
      </b-autocomplete>
    </b-field>
    <b-button class="is-primary" @click="requestChoreHistory">Search</b-button>
  </section>
</template>

<script>
const values = [
  {
    "value": "Hissan"
  },
  {
    "value": "Daniel"
  }
];

const validFields = [
  {
    "fieldDisplayName": "User Name",
    "fieldName": "completed_by"
  },
  {
    "fieldDisplayName": "Chore Name",
    "fieldName": "chore_name"
  }
]

import axios from 'axios';

export default {
  name: "ChoreHistorySearch",
  data () {
    return {
      values: values,
      validFields: validFields,
      name: "",
      filterField: "",
      filterTerm: ""
    }
  },
  methods: {
    requestChoreHistory() {
      axios.get("http://127.0.0.1:8003/chore/history", {
        params: {
          filter_term: this.filterTerm,
          filter_field: this.filterField
        }
      })
      .then(response => {
        console.log(response);
      })
    }
  },
  computed: {
  }
}
</script>

<style scoped lang="scss">

</style>
