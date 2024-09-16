
<body>

    <nav class="navbar navbar-expand-lg bg-body-tertiary   w-100  " style="background-color: #10c13c;
    background-image: linear-gradient(90deg, #17b117 35%, #238f1e 100%);
    ">
        <div class="container-fluid">
            <a class="navbar-brand  text-light mx-3 fs-1 fw-italic" href="#">Crop-Monitoring</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse"
                data-bs-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false"
                aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarSupportedContent">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <li class="nav-item">
                        <a class="nav-link active    text-light fs-1" aria-current="page"
                            href="{{ url_for('login') }}">Login</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link active text-light" href="{{ url_for('signup') }}">Signup</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link active text-light" href="{{ url_for('login_admin') }}">admin</a>
                    </li>
            </div>
            <form class="d-flex" role="search">
                <input class="form-control me-2" type="search" placeholder="Search" aria-label="Search">
                <button class="btn btn-dark mx-3" type="submit">Search</button>
            </form>
        </div>
    </nav>
    <div class="mh-100"
        style="width: 100%; height: 500px; background-color: rgba(148, 148, 148, 0.1); background-image: url(./static/R.jpeg); background-size: cover;">
        <div class="container">
            <center>
                <h1 class="" style="font-size: 48px;  padding-top: 55px; color: aliceblue;">Satellite-Crop-Monitoring
                </h1>
            </center>
        </div>
    </div>

    <div class="card text-center">
        <div class="card-header">
            Featured
        </div>
        <div class="card-body">
            <h5 class="card-title">Crop-Monitoring</h5>
            <p class="card-text">With supporting text below as a natural lead-in to additional content.</p>
            <a href="{{ url_for('login') }}" class="btn  text-white" style="background-color: #10c163;
            background-image: linear-gradient(90deg, #10c163 35%, #0eff00 100%);
            ">Login</a>
        </div>
        <div class="card-footer text-body-secondary">
            <a href="{{ url_for('signup') }}" class="text-dark ">join us</a>
        </div>
    </div>


    <div class="container my-4">
        <center>
            <h1>ABOUT US</h1>
            <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Consequuntur consectetur ex molestiae
                dignissimos,
                ut perferendis architecto magnam omnis animi quam officiis quidem corporis cumque minima ea atque
                reiciendis
                magni ipsam sint, nobis minus odit eaque est libero! Quis tempora facilis ducimus, quae esse incidunt,
                nulla
                aliquam error vel eum harum ullam reprehenderit sunt maiores corporis alias quia magni veritatis
                exercitationem tempore quam ipsam laborum. Laudantium, tempore dolores et tempora aliquam animi
                voluptate
                saepe facilis ducimus possimus, aut ut quo velit a incidunt, odio quibusdam nesciunt. Minima animi
                aperiam
                culpa magni facere beatae rem dolores fugit veniam corporis? Cum, dolore vero.</p>

            <p>Lorem ipsum dolor sit amet consectetur adipisicing elit. Consequuntur consectetur ex molestiae
                dignissimos,
                ut perferendis architecto magnam omnis animi quam officiis quidem corporis cumque minima ea atque
                reiciendis
                magni ipsam sint, nobis minus odit eaque est libero! Quis tempora facilis ducimus, quae esse incidunt,
                nulla
                aliquam error vel eum harum ullam reprehenderit sunt maiores corporis alias quia magni veritatis
                exercitationem tempore quam ipsam laborum. Laudantium, tempore dolores et tempora aliquam animi
                voluptate
                saepe facilis ducimus possimus, aut ut quo velit a incidunt</p>

        </center>


        <footer class="py-3 my-4 ">
            <ul class="nav justify-content-center border-bottom pb-3 mb-3">
                <li class="nav-item"><a href="#" class="nav-link px-2 text-muted">Home</a></li>
                <li class="nav-item"><a href="#" class="nav-link px-2 text-muted">Features</a></li>
                <li class="nav-item"><a href="#" class="nav-link px-2 text-muted">Pricing</a></li>
                <li class="nav-item"><a href="#" class="nav-link px-2 text-muted">FAQs</a></li>
                <li class="nav-item"><a href="#" class="nav-link px-2 text-muted">About</a></li>
            </ul>
            <p class="text-center text-muted">© 2024 lab Automation, Inc</p>
        </footer>

    </div>
</body>


<script src="https://cdn.jsdelivr.net/npm/popper.js@1.14.7/dist/umd/popper.min.js"
    integrity="sha384-UO2eT0CpHqdSJQ6hJty5KVphtPhzWj9WO1clHTMGa3JDZwrnQq4sF86dIHNDz0W1"
    crossorigin="anonymous"></script>


<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/js/bootstrap.min.js"
    integrity="sha384-JjSmVgyd0p3pXB1rRibZUAYoIIy6OrQ6VrjIEaFf/nJGzIxFDsf4x0xIM+B07jRM"
    crossorigin="anonymous"></script>

</html>