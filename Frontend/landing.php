<html>
        <head>
                <title> ShapeShift </title>
                <link rel="stylesheet" href="index.css" />
        </head>
  
        <body style="color:#008080;" >
                <h1 class="welcome">
                        <img class="img2" src="logo.png">
                        <a href="http://10.248.179.10:7007/login.html">
                                <img class="img3" src="logout.png" style="width:5%; padding-right: 1%">
                        </a>
                        WELCOME TO SHAPESHIFT <br>
                        <p class="mantra">SHIFT YOUR HEALTH, SHAPE YOUR FUTURE</p> 
                        <div align="right" style="font-size:20px; font-style:normal">
                                Logout, 
                                <?php echo $_POST["email"]; ?>
                        </div>
                </h1>
                
                <p style="font-size:30px">
                        TODAY: <script> document.write(new Date().toDateString()); </script>
                </p>
                
                <div class="parent"> 
                <p style="font-size:20px; color:black"> Calories Intake: <?php echo "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" ?> Protein Intake: <?php echo "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" ?> Carbs Intake: <?php echo "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" ?> Fiber Intake: <?php echo "&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;" ?> </p> 
                        <div class="circle"> 878 / 1600 </div>
                                <?php echo "&nbsp;&nbsp;" ?>
                        <div class="circle"> 45 / 120 g  </div>
                                <?php echo "&nbsp;&nbsp;" ?>
                        <div class="circle"> 190 / 325 g </div>
                                <?php echo "&nbsp;&nbsp;" ?>
                        <div class="circle"> 10 / 30 g </div>
                                <?php echo "&nbsp;&nbsp;" ?>
                </div>

        <?php
                echo "hi ";
                echo $_POST["email"];
        ?>
        </body>
</html>