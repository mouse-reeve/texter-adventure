angular.module('gameFactory', []).factory('Game', function($http) {
    return {
        startGame: function(name, phone) {
            return $http.get('/api/start/' + name + '/' + phone).then(function(response) {
                return response.data;
            });
        },

        sendTurn: function(turnData, phone) {
            return $http.post('/api/send/' + phone, turnData).then(function(response) {
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
