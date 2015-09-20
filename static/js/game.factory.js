angular.module('gameFactory', []).factory('Game', function($http) {
    return {
        startNewGame: function(name, phone) {
            return $http.get('/api/start/' + name + '/' + phone).then(function(response) {
                return response.data;
            });
        },

        sendTurn: function(turnData, phone) {
            return $http.post('/api/send/' + phone, turnData).then(function(response) {
                return response.data;
            });
        },

        getGames: function() {
            return $http.get('/api/games').then(function(response) {
                return response.data;
            });
        },

        // for test only
        sendResponse: function(option) {
            var smsData = {'Body': 'A', 'From': '15005550006'};
            return $http.post('/api/respond', smsData).then(function(response) {
                return response.data;
            });
        },
    };
});
