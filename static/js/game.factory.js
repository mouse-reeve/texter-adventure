angular.module('gameFactory', []).factory('Game', function($http) {
    return {
        startGame: function() {
            return $http.get('/api/start').then(function(response) {
                return response.data;
            });
        },

        sendTurn: function(turnData) {
            return $http.post('/api/send', turnData).then(function(response) {
                return response.data;
            });
        },

        sendResponse: function(option, turnData) {
            return $http.post('/api/respond/' + option, turnData).then(function(response) {
                return response.data;
            });
        },
    };
});
