angular.module('app', ['gameFactory', 'ngRoute']).config(function ($httpProvider, $locationProvider, $routeProvider) {
    $routeProvider
        .when('/', {
            controller: 'MainController',
            templateUrl: 'static/partials/main.html'
        })
        .otherwise({
            redirectTo: '/'
        });

    $locationProvider.html5Mode(true);


    $httpProvider.interceptors.push(function($q) {
        return {
            'response': function(response) {
                var deferred = $q.defer();

                if (response.config.url.startsWith('/api/')) {
                    if (response.data.success) {
                        deferred.resolve(response.data);
                    } else {
                        deferred.reject(response.data);
                    }
                    return deferred.promise;
                }
                return response;
            }
        };
    });
});

