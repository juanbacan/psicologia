var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
    return new bootstrap.Tooltip(tooltipTriggerEl)
});

function fetchRequest(options) {
    return new Promise((resolve, reject) => {
        let url = options.url;
        headers = {'Content-Type': 'application/json', 'X-CSRFToken': csrf_token};
        if (options.headers) headers = Object.assign(headers, options.headers);
        let init = { method: options.method || 'GET', headers: headers };
        
        if (options.data) {
            if (init.method === 'GET') {
                url += '?' + new URLSearchParams(options.data).toString();
            } else {
                init.body = JSON.stringify(options.data);
                init.headers['Content-Type'] = 'application/json';
            }
        }
        if (options.timeout) init.timeout = options.timeout;

        fetch(url, init)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => Promise.reject(data));
                }
                return response.json();
            })
            .then(data => {
                if (options.success) {
                    options.success(data);
                } else {
                    resolve(data);
                }
            })
            .catch(error => {
                if (options.error) {
                    options.error(error);
                } else {
                    reject(error);
                }
            });
        });
}

function fetchRequest2(options) {
    return new Promise((resolve, reject) => {
        let url = options.url;
        headers = {'Content-Type': 'application/json', 'X-CSRFToken': csrf_token};
        if (options.headers) headers = Object.assign(headers, options.headers);
        let init = { method: options.method || 'GET', headers: headers };
        
        if (options.data) {
            if (init.method === 'GET') {
                url += '?' + new URLSearchParams(options.data).toString();
            } else {
                init.body = JSON.stringify(options.data);
                init.headers['Content-Type'] = 'application/json';
            }
        }
        if (options.timeout) init.timeout = options.timeout;

        fetch(url, init)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(data => Promise.reject(data));
                }
                return response.json();
            })
            .then(data => {
                if (options.success) {
                    options.success(data);
                } else {
                    resolve(data);
                }
            })
            .catch(error => {
                if (options.error) {
                    options.error(error);
                } else {
                    reject(error);
                }
            });
        });
}

// Main *****************************************
function ready(callback){
    // in case the document is already rendered
    if (document.readyState!='loading') callback();
    // modern browsers
    else if (document.addEventListener) document.addEventListener('DOMContentLoaded', callback);
    // IE <= 8
    else document.attachEvent('onreadystatechange', function(){
        if (document.readyState=='complete') callback();
    });
}

function bloqueoInterfaz() {
    // console.log("Bloqueando Interfaz");
    document.getElementById( 'loading-static' ).style.display = 'flex';
}
function desbloqueoInterfaz() {
    // console.log("Desbloqueando Interfaz");
    document.getElementById( 'loading-static' ).style.display = 'none';
}

function showErrorMessage(mensaje="Ha ocurrido un error inesperado en el servidor", titulo="Error") {
    document.getElementById('error-title').innerHTML = titulo;
    document.getElementById('error-message').innerHTML = mensaje;
    document.getElementById( 'error-static' ).style.display = 'flex';
}

function hideErrorMessage() {
    document.getElementById( 'error-static' ).style.display = 'none';
}

function showToastMessage({
    mensaje = "Aquí debes poner un mensaje", 
    titulo = "Aquí debes poner un título", 
    delay = 3000, 
    color = "primary"} = {},
    ) {

    const colorToast = "text-bg-" + color;
    document.getElementById('custom-toast-title').innerHTML = titulo;
    document.getElementById('custom-toast-message').innerHTML = mensaje;
    const toast = document.getElementById('customToast');
    toast.classList.remove('text-bg-primary', 'text-bg-secondary', 'text-bg-success', 'text-bg-danger', 'text-bg-warning', 'text-bg-info', 'text-bg-light', 'text-bg-dark');
    toast.classList.add(colorToast);
    const toastInstance = new bootstrap.Toast(toast, {delay: delay, animation: true});
    toastInstance.show();
}

async function handleResponse(resp, data, modalName='modalEdicion') {
    if (resp.ok){
        const scripts = data.match(/<script[^>]*>([\s\S]*?)<\/script>/gi);
        const dataClean = data.replace(scripts, '');
        const modalEdicion = document.getElementById(modalName);
        modalEdicion.innerHTML = dataClean;
        const myModal = new bootstrap.Modal(modalEdicion);
        myModal.show();
        if(!scripts) return;
        const tagWhiteList = ["<img", "<iframe", "img.src", "iframe.src"];
        scripts.forEach(script => {
            const isInWhitelist = tagWhiteList.some(tag => script.includes(tag));
            if (script.includes('src') && !isInWhitelist) {
                try{
                    const src = script.match(/src="([^"]*)"/)[1];
                    const newScript = document.createElement('script');
                    newScript.src = src;
                    document.body.appendChild(newScript);
                    loadedScripts.push(src);
                } catch {
                    console.log('Error al cargar el script');
                }
            } else {
                try{
                    const scriptClean = script.replace(/<script[^>]*>|<\/script>/gi, '');
                    const newScript = document.createElement('script');
                    newScript.innerHTML = scriptClean;
                    modalEdicion.appendChild(newScript);
                    loadedScripts.push(scriptClean);
                } catch {
                    console.log('Error al cargar el script');
                }
            }
        });
    } else{
        desbloqueoInterfaz();
    }
}

let loadedScripts = [];
const modals = document.getElementsByClassName('formmodal');
for (let i = 0; i < modals.length; i++) {
    modals[i].addEventListener('click', async function(e) {
        try {
            e.preventDefault()
            const nhref = modals[i].getAttribute('nhref');
            if (!nhref) return;
            bloqueoInterfaz();
            console.log('Cargando formulario desde servidor');
            const resp = await fetch(nhref);
            // Cierra cualquier modal abierto
            const data = await resp.text();
            const modal = document.querySelector('.modal.show');
            if (modal) {
                const modalBS = bootstrap.Modal.getInstance(modal);
                modalBS.hide();
            }
            /*console.log('Formulario guardado en caché');*/
            handleResponse(resp, data);            
            desbloqueoInterfaz();
        } catch{
            // console.log('Error al cargar el formulario')
            desbloqueoInterfaz();
        }
    })
}

// Función para enviar un formulario dinámico en modal
const submitModalForm1 = async (formid = 'modalForm1', showError = true) => {
    const form = document.getElementById(formid);
    //if (!form.reportValidity()) return;
    form.classList.add('was-validated')
    
    if (!form.checkValidity()) return;

    bloqueoInterfaz();
    const resp = await fetch(form.getAttribute('action'), {
        method: 'POST',
        body: new FormData(form)
    });
    // Error en el servidor 
    if (resp.status !== 200) {
        desbloqueoInterfaz();
        const data = await resp.json();
        if (showError) showErrorMessage(data.mensaje || 'Ha ocurrido un error inesperado en el servidor 200');
        return {result: 'error'};
    }

    const data = await resp.json();
    
    if (data.result == "ok") {
        if (data.redirected) {
            try{
                var currentUrl = window.location.href.split('#')[0];
                // Comparar con la nueva URL
                if (currentUrl === data.url) {
                    // Si la URL es la misma, recargar la página
                    location.reload();
                } else {
                    // Si la URL es diferente, redirigir a la nueva URL
                    location.href = data.url;
                }
            } catch {
                window.location.replace(data.url);
            }
        } else {
            const myModal = bootstrap.Modal.getInstance(document.getElementById('modalEdicion')); 
            // Check if the modal is open
            if (myModal) myModal.hide();
            desbloqueoInterfaz();
            return data;
        }

z
    } else if (data.result == "error") {
        if(data.form){
            try{
                const contentModalForm = document.getElementById('form-render-modal');
                contentModalForm.innerHTML = data.form;
                form.classList.remove('was-validated');
            } catch {
                console.log('No se pudo actualizar el formulario');
            }
        }
        desbloqueoInterfaz();

        if (showError) showErrorMessage(data.mensaje || 'Ha ocurrido un error inesperado en el servidor');
        return data;
    }
}
// Bloquear la interfaz al enviar un formulario
// Get all form
const forms = document.getElementsByTagName('form');
for (let i = 0; i < forms.length; i++) {
    forms[i].addEventListener('submit', function(e) {
        bloqueoInterfaz();
    })
}

// Búsqueda

document.querySelectorAll(".form-select-custom").forEach(function (select) {
    const input = select.querySelector(".form-select-custom-input");
    const optionsList = select.querySelector(".form-select-custom-options");
  
    input.addEventListener("click", function () {
        
        // If optionsList is empty, don't show it
        if (optionsList.innerHTML === '') return;

        select.classList.toggle("show");
    });
  
    input.addEventListener("input", debounce(async function () {
        const inputValue = input.value.trim().toLowerCase();

        if (inputValue === '' || inputValue.length < 3) {
            optionsList.innerHTML = '';
            select.classList.remove('show');
            return;
        }
        
        // Si el input está vacío, ocultar la lista de opciones y salir de la función
        if (inputValue === '') {
            optionsList.innerHTML = '';
            select.classList.remove('show');
            return;
        }

        // Llamar a la API y obtener los productos
        // const response = await fetchRequest('/api/', {'action': 'search_cursos', 'query': inputValue}, csrf_token);
        fetchRequest({
            url: url_ecommerce,
            method: 'POST',
            data: {
                action: 'search_cursos',     
                query: inputValue
            },
            success: function (response) {
                console.log(response);
                const data = response.resp.list_cursos;
                if (data.length > 0) {
                    optionsList.innerHTML = '';
                    select.classList.add('show');
                }
        
                if (data.length === 0) {
                    console.log('No se encontraron resultados');
                    const option = document.createElement('li');
                    option.classList.add('form-select-custom-option');
                    option.innerHTML = `
                        <div class="row py-3">
                            <div class="col-12">
                                <p class="mb-0">No se encontraron resultados</p>
                            </div>
                        </div>
                    `;
                    optionsList.appendChild(option);
                }
                
                // Generar elementos <li> para cada producto y agregarlos a la lista de opciones
                const options = data.map(institucion => {
                    const option = document.createElement('li');
                    option.classList.add('form-select-custom-option');
                    option.dataset.value = institucion.id;
                    option.innerHTML = `
                        <a href="/ecommerce/producto/${institucion.slug}/" style="text-decoration: none; color: inherit;">
                            <div class="row my-2">
                                <div class="col-4">
                                    <img src="${institucion.imagen}" class="img-fluid" alt="${institucion.nombre}">
                                </div>
                                <div class="col-8">
                                    <div class="col-12">
                                        <h6 class="mb-0">${institucion.nombre}</h6>
                                    </div>
                                    <div class="col-12">
                                        <p class="mb-0 text-muted"><small>Curso ${institucion.tipo}<small></p>
                                    </div>
                                </div>
                            </div>
                        </a>
                    `;
                    return option;
                });
        
                // Limitar la cantidad de opciones que se muestran en la lista
                const MAX_OPTIONS = 20;
                options.slice(0, MAX_OPTIONS).forEach(option => optionsList.appendChild(option));
                
                // Si hay más opciones que la cantidad máxima permitida, agregar un mensaje indicando esto
                if (options.length > MAX_OPTIONS) {
                    const moreOptions = document.createElement('li');
                    moreOptions.textContent = `Mostrando ${MAX_OPTIONS} de ${options.length} opciones`;
                    moreOptions.classList.add('form-select-custom-more-options');
                    optionsList.appendChild(moreOptions);
                }
        
                // Mostrar la lista de opciones y actualizar el valor seleccionado en el dataset
                select.dataset.selectedValue = '';
                select.classList.add('show');
            }
        })
    }, 500));
  
    document.addEventListener("click", function (event) {
        if (!select.contains(event.target)) {
            select.classList.remove("show");
        }
    });
});

function debounce(fn, delay) {
    let timeoutId;
    return function (...args) {
        if (timeoutId) clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
            fn.apply(this, args);
        }, delay);
    };
}







