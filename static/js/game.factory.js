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

        getHistory: function(phone) {
            return $http.get('/api/history/' + phone).then(function(response) {
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
