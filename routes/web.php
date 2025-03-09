<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\HomeController;

Route::get('/', function () {
   
});

Route::get('/posts', function () {
    return "Aquí se mostrarán todos los posts";
});

Route::get('/posts/create', function () {
    return "Aquí se mostrará un formulario para crear un post";
});
