angular.module('app', ['ngRoute'])
    .config(function ($locationProvider, $routeProvider) {

        $routeProvider
            .when('/', {
                controller: 'MainController',
                templateUrl: 'static/partials/main.html'
            })
            .otherwise({
                redirectTo: '/'
            });

        $locationProvider.html5Mode(true);
    });

