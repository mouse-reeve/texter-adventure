angular.module('gameFactory', []).factory('Game', function($http) {
    return {
        startNewGame: function() {
            return $http.get('/api/player/new').then(function(response) {
                return response.data;
            });
        },

        addPlayer: function(name, phone) {
            return $http.post('/api/player', {'name': name, 'phone': phone}).then(function(response) {
                return response.data;
            });
        },

        sendTurn: function(turnData, phone) {
            return $http.post('/api/message/' + phone, turnData).then(function(response) {
                return response.data;
            });
        },

        getGames: function() {
            return $http.get('/api/player').then(function(response) {
                return response.data;
            });
        },

        setUID: function(uid, phone){
            return $http.put('/api/player/' + phone + '/' + uid).then(function(response) {
                return response.data;
            });
        },

        update: function(phone, changedData) {
            return $http.put('/api/player/' + phone, changedData).then(function(response) {
                return response.data;
            });
        },
    };
});
