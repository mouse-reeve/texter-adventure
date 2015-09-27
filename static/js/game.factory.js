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

        setUID: function(uid, phone){
            return $http.put('/api/uid/' + phone + '/' + uid).then(function(response) {
                return response.data;
            });
        },

        setName: function(name, phone) {
            return $http.put('/api/name/' + phone + '/' + name).then(function(response) {
                return response.data;
            });
        },

        hide: function(phone) {
            return $http.put('/api/visibility/' + phone);
        },

        // for test only
        sendResponse: function(option, phone) {
            var smsData = {'Body': option, 'From': phone};
            return $http.post('/api/respond', smsData).then(function(response) {
                return response.data;
            });
        },
    };
});
