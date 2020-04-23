var app = angular.module('statisticsmaps', []);

app.config(['$httpProvider', function($httpProvider) {
  $httpProvider.defaults.xsrfCookieName = 'csrftoken';
  $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
}]);

app.controller('statistics', ['$scope',
  function($scope) {

    // dashboard variables
    $scope.total_cases = true;
    $scope.total_deaths = false;
    $scope.new_cases = false;
    $scope.new_deaths = false;
    $scope.active_cases = false;

    $scope.statistic_type = 'total_cases'

    $scope.set_statistic_type = function(event) {
      if (event == 'total_cases') {
        $scope.total_cases = true;
        $scope.total_deaths = false;
        $scope.new_cases = false;
        $scope.new_deaths = false;
        $scope.active_cases = false;
      } else if (event == 'total_deaths') {
        $scope.total_cases = false;
        $scope.total_deaths = true;
        $scope.new_cases = false;
        $scope.new_deaths = false;
        $scope.active_cases = false;
      } else if (event == 'new_cases') {
        $scope.total_cases = false;
        $scope.total_deaths = false;
        $scope.new_cases = true;
        $scope.new_deaths = false;
        $scope.active_cases = false;
      } else if (event == 'new_deaths') {
        $scope.total_cases = false;
        $scope.total_deaths = false;
        $scope.new_cases = false;
        $scope.new_deaths = true;
        $scope.active_cases = false;
      } else if (event == 'active_cases') {
        $scope.total_cases = false;
        $scope.total_deaths = false;
        $scope.new_cases = false;
        $scope.new_deaths = false;
        $scope.active_cases = true;
      };
    };

  }
]);
