<?php
session_start();

date_default_timezone_set("Europe/Berlin");


function clean($str){
    $str = mb_convert_encoding($str, 'UTF-8', 'UTF-8');
    $str = htmlentities($str, ENT_QUOTES, 'UTF-8');
    return $str;
}

if(isset($_POST['submit'])){

    $password = clean($_POST['password']);

    // If username and password are not empty
    if ($password != ""){
        if ($password == $_ENV['password']) {
            $_SESSION['passwd'] = $_ENV['password'];
        } else {
            echo "Error! Invalid username and password.";
        }
    } else {
    
    // Display failed message
            echo "Error! Invalid username and password.";
    }

}
?>

<!DOCTYPE HTML>
<html lang="en">
    <head>
        <meta charset="utf-8" />
        <title>WALL-E</title>
        <meta name="description" content="Website of the WALL-E-Project">
        <meta name="author" content="Timo Bilhöfer">
        <link rel="icon" type="image/png" href="img/mov.png">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no" />
        <link rel="stylesheet" href="css/styles.css" />
    </head>
    <body>


<?php

if (!isset($_SESSION['passwd'])){
    ?>
    <form method="post" action="">
        <div id="div_login">
            <h1>Login</h1>
            <div>
                <input type="password" class="textbox" id="password" name="password" placeholder="Password"/>
            </div>
            <div>
                <input type="submit" value="Submit" name="submit" id="submit" />
            </div>
        </div>
    </form>
    <?php
} elseif ($_SESSION['passwd']) {

?>
        <header>
            <form action="<?php echo $_ENV['APIURL'] ?>/backup/"  method="post" class="headerForm" id="backupForm" enctype="multipart/form-data">
                <input type="hidden" name="password" value="<?php echo $_SESSION['passwd']; ?>"/>
                <span class="headerIcon">&#x1F4BE;</span>
            </form>
            <form action="<?php echo $_ENV['APIURL'] ?>/power/"  method="post" class="headerForm" id="powerForm" enctype="multipart/form-data">
                <input type="hidden" name="password" value="<?php echo $_SESSION['passwd']; ?>"/>
                <span class="headerIcon">&#x1F50C;</span>
            </form>
        </header>
        <div id="main">
            <h1>WALL-E</h1>
            <p>Select upload type:</p>
            <div id="ulType">
                <button id="bImgUl">Image upload</button>
                <button id="bVidUl">Video upload</button>
                <button id="bDrawUl">Drawing</button>
            </div>
            <div id="imgUl" class="hidden ul">
                <form action="<?php echo $_ENV['APIURL'] ?>/upload/" method="post" class="ulForm" enctype="multipart/form-data"> 
                    <label>Select a file: <input type="file" name="in_file"/></label>
                    <label>How long should the image be shown: <select name="length">
                        <option value="10">10s</option>
                        <option value="20">20s</option>
                        <option value="30">30s</option>
                    </select></label> 
                    <label>Daily recurring image: <input type="checkbox" value="1" name="recurring"/></label>
                    <label>When should the image be shown (leave empty for ASAP): <input type="time" name="time" /></label>
                    <input type="hidden" name="password" value="<?php echo $_SESSION['passwd']; ?>"/>
                    <input type="submit" value="Upload" />               
                </form>
                <div class="ulStatus">
                    <img src="" class="loading hidden" alt="loading" />
                    <p class="responseText"><p>
                </div>
            </div>
            <div id="vidUl" class="hidden ul">
                <form action="<?php echo $_ENV['APIURL'] ?>/upload/"  method="post" class="ulForm" enctype="multipart/form-data">
                    <label>Select a file: <input type="file" name="in_file"/></label>
                    <label>Daily recurring video: <input type="checkbox" value="1" name="recurring" /></label>
                    <label>When should the video be shown (leave empty for ASAP): <input type="time" name="time" /></label>
                    <input type="hidden" name="password" value="<?php echo $_SESSION['passwd']; ?>"/>
                    <input type="submit" value="Upload" />
                </form>
                <div class="ulStatus">
                    <img src="" class="loading hidden" alt="loading" />
                    <p class="responseText"><p>
                </div>
            </div>
            <div id="drawUl" class="hidden ul">
                <p>Coming soon...</p>
            </div>
            <h2>Queue:</h2>
            <div id="queueDiv">
                
                <?php
                    $queue = json_decode(file_get_contents('http://'.$_SERVER['SERVER_NAME'].$_ENV['APIURL']."/queue/"), true);
                    if ($queue != ""){
                        foreach ($queue as $qMov) {
                            $qmFilename = explode("/", $qMov["filePath"]);
                            ?>
                            <div class="qMov">
                                <img src="/img/mov.png" alt="Movie-Thumbnail" class="movThumb">
                                <div class="qmInfo">
                                    <?php
                                    echo "<p>".end($qmFilename)."</p>";
                                    echo "<p>".date("H:i - d.m.y",$qMov["dTime"])."</p>"; 
                                    ?>
                                </div>
                                <form action="<?php echo $_ENV['APIURL'] ?>/delQueue"  method="post" class="delForm" enctype="multipart/form-data">
                                    <input type="hidden" name="movName" value="<?php echo $qMov["filePath"] ?>" />
                                    <input type="hidden" name="password" value="<?php echo $_SESSION['passwd']; ?>"/>
                                    <span class="delMov">&#x1f5d1;</span>
                                </form>
                            </div>
                            <?php
                        }
                    }

                ?>
            </div>
        </div>
        <script src="js/jquery-3.6.0.min.js"></script>
        <script src="js/main.js"></script>

<?php
};

?>

</body>
</html>

<?php

die();