<template>
  <section>
    <b-field>
      <b-input placeholder="Filter results..."
               v-model="filterTerm"
               type="search"
               icon="magnify"
               @input="fetchChoreHistory"
               rounded
               >
      </b-input>
    </b-field>
    <b-table
        :data="data"
        :loading="loading"
        :total="total"
        paginated
        backend-pagination
        :per-page="perPage"
        @page-change="onPageChange"
        aria-next-label="Next page"
        aria-previous-label="Previous page"
        aria-page-label="Page"
        aria-current-label="Current page"

        backend-sorting
        :default-sort-direction="defaultSortOrder"
        :default-sort="[sortField, sortOrder]"
        @sort="onSort"

    >
      <b-table-column field="completed_by" label="Completed By" sortable v-slot="props">
        {{ props.row.completed_by }}
      </b-table-column>

      <b-table-column field="chore_name" label="Chore Name" sortable v-slot="props">
        {{ props.row.chore_name }}
      </b-table-column>

      <b-table-column field="completion_date" label="Completion Date" sortable v-slot="props">
        {{ props.row.completion_date ? new Date(props.row.completion_date).toLocaleDateString() : 'unknown' }}
      </b-table-column>

    </b-table>
  </section>
</template>

<script>
import axios from 'axios';

export default {
  name: "ChoreHistoryTable",
  data() {
    return {
      data: [],
      loading: false,
      perPage: 10,
      total: 0,
      page: 1,
      sortField: 'completion_date',
      sortOrder: 'desc',
      defaultSortOrder: 'desc',
      filterTerm: '',
      fetching: false,
      cancelToken: null
    }
  },
  methods: {
    fetchChoreHistory() {
      if (this.cancelToken !== null) this.cancelToken.cancel();

      const cancelTokenSource = axios.CancelToken.source();
      this.cancelToken = cancelTokenSource

      this.loading = true;
      axios.get("http://127.0.0.1:8003/chore/history", {
        params: {
          filterTerm: this.filterTerm,
          sortField: this.sortField,
          sortOrder: this.sortOrder,
          count: this.perPage,
          offset: (this.page - 1) * this.perPage,
        },
        cancelToken: cancelTokenSource.token
      })
      .then((response) => {
        this.data = []; // reset the data
        this.total = response.data.document_count;
        response.data.documents.forEach( (item) => {
          item.completed_by = this.capitalizeString(item.completed_by);
          item.chore_name = this.capitalizeString(item.chore_name);
          this.data.push(item);
        })
      })
      this.loading = false;
    },
    onPageChange(page) {
      this.page = page;
      this.fetchChoreHistory();
    },
    onSort(field, order) {
      this.sortField = field;
      this.sortOrder = order;
      this.fetchChoreHistory();
    },
    capitalizeString(str) {
      return str.charAt(0).toUpperCase() + str.slice(1);
    }
  },
  mounted() {
    this.fetchChoreHistory();
  }
}
</script>

<style scoped>

</style>
