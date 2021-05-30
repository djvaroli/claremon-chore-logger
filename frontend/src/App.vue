<template>
  <div id="app" class="container">
    <ChoreHistoryTable />
  </div>
</template>

<script>
// import ChoreHistorySearch from "./components/ChoreHistorySearch";
import ChoreHistoryTable from "./components/ChoreHistoryTable";

export default {
  name: 'App',
  components: {
    ChoreHistoryTable
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
