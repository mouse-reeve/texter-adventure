angular.module('gameFactory', []).factory('Game', function($http) {
    return {
        startNewGame: function() {
            return $http.get('/api/player/new').then(function(response) {
                return response.data.data;
            });
        },

        addPlayer: function(name, phone) {
            return $http.post('/api/player', {'name': name, 'phone': phone}).then(function(response) {
                return response.data.data;
            });
        },

        sendTurn: function(turnData, phone) {
            return $http.post('/api/send/' + phone, turnData).then(function(response) {
                return response.data.data;
            });
        },

        getGames: function() {
            return $http.get('/api/player').then(function(response) {
                return response.data.data;
            });
        },

        setUID: function(uid, phone){
            return $http.put('/api/uid/' + phone + '/' + uid).then(function(response) {
                return response.data.data;
            });
        },

        setName: function(name, phone) {
            return $http.put('/api/name/' + phone + '/' + name).then(function(response) {
                return response.data.data;
            });
        },

        hide: function(phone) {
            return $http.put('/api/visibility/' + phone);
        },

        // for test only
        sendResponse: function(option, phone) {
            var smsData = {'Body': option, 'From': phone};
            return $http.post('/api/respond', smsData).then(function(response) {
                return response.data.data;
            });
        },
    };
});
