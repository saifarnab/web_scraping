<?php
$conn = mysqli_connect("localhost","root","") or die("Cant connect to server!"); 
mysqli_select_db($conn,"marketplace") or die("Cant connect to database!");

$file_path = "listings.txt";
$data = file($file_path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);

$profile_bgs = [
    'profile-bg-weave',
    'profile-bg-stairs',
    'profile-bg-arrows',
    'profile-bg-zigzag',
    'profile-bg-carbon',
    'profile-bg-cross',
    'profile-bg-paper',
    'profile-bg-waves',
    'profile-bg-tablecloth',
    'profile-bg-seigaiha',
    'profile-bg-jcubes',
    'profile-bg-bricks',
    'profile-bg-checkerboard',
    'profile-bg-starrynight',
    'profile-bg-stars',
    'profile-bg-wave',
    'profile-bg-blueprint'
];

$levels = [
    1 => 0,
    2 => 30000,
    3 => 60000,
    4 => 90000,
    5 => 180000,
    6 => 360000,
    7 => 720000,
    8 => 1500000,
];

foreach ($data as $line) {
    $values = explode(":", $line);

    $listingId = mysqli_real_escape_string($conn,$values[0]);
    $title = mysqli_real_escape_string($conn,$values[1]);
    $vendorId = mysqli_real_escape_string($conn,$values[2]);
    $vendor = mysqli_real_escape_string($conn,$values[3]);
    $categoryId = mysqli_real_escape_string($conn,$values[4]);
    $subCategoryId = mysqli_real_escape_string($conn,$values[5]);
    $price = mysqli_real_escape_string($conn,$values[6]);
    $quantity = mysqli_real_escape_string($conn,$values[7]);
    $type = mysqli_real_escape_string($conn,$values[8]);
    $shippingFrom = mysqli_real_escape_string($conn,$values[9]);
    $shippingTo = mysqli_real_escape_string($conn,$values[10]);
    $description = mysqli_real_escape_string($conn,$values[11]);

    if($price=="")
    {
        $price = 100.00;
    }
    if($quantity=="")
    {
        $quantity = 100;
    }
    
    $conn->query("SET FOREIGN_KEY_CHECKS = 0");

    $sql = "INSERT INTO PRODUCTS (id, name, description, rules, quantity, mesure, active, coins, category_id, user_id, created_at, updated_at, types)
        VALUES ('$listingId', '$title', '$description', 'No rules', '$quantity', '$price', '1', 'btc', '$categoryId', '$vendorId', NOW(), NOW(), 'all')
        ON DUPLICATE KEY UPDATE name=VALUES(name), description=VALUES(description), rules=VALUES(rules), quantity=VALUES(quantity), mesure=VALUES(mesure), active=VALUES(active), coins=VALUES(coins), category_id=VALUES(category_id), user_id=VALUES(user_id), created_at=VALUES(created_at), updated_at=VALUES(updated_at), types=VALUES(types)";
    $conn->query($sql);

    $sql1 = "INSERT INTO PHYSICAL_PRODUCTS (id, countries_option, countries, country_from, created_at, updated_at)
        VALUES ('$listingId', 'all', ' ', '$shippingFrom', NOW(), NOW())
        ON DUPLICATE KEY UPDATE countries_option=VALUES(countries_option), countries=VALUES(countries), country_from=VALUES(country_from), created_at=VALUES(created_at), updated_at=VALUES(updated_at)";
    $conn->query($sql1);

    $sql2 = "INSERT INTO IMAGES (id, product_id, image, first, created_at, updated_at)
        VALUES ('$listingId', '$listingId', ' ', 0, NOW(), NOW())
        ON DUPLICATE KEY UPDATE product_id=VALUES(product_id), image=VALUES(image), first=VALUES(first), created_at=VALUES(created_at), updated_at=VALUES(updated_at)";
    $conn->query($sql2);

    $sql3 = "INSERT INTO OFFERS (id, product_id, min_quantity, price, created_at, updated_at, deleted)
        VALUES ('$listingId', '$listingId', 1, '$price', NOW(), NOW(), 'NO')
        ON DUPLICATE KEY UPDATE product_id=VALUES(product_id), min_quantity=VALUES(min_quantity), price=VALUES(price), created_at=VALUES(created_at), updated_at=VALUES(updated_at), deleted=VALUES(deleted)";
    $conn->query($sql3);

    $sql4 = "INSERT INTO SHIPPINGS (id, product_id, name, price, duration, from_quantity, to_quantity, created_at, updated_at, deleted)
        VALUES ('$listingId', '$listingId', '1 Day', '17.99', '24 hours', 1, '$quantity', NOW(), NOW(), 'NO')
        ON DUPLICATE KEY UPDATE product_id=VALUES(product_id), name=VALUES(name), price=VALUES(price), duration=VALUES(duration), from_quantity=VALUES(from_quantity), to_quantity=VALUES(to_quantity), created_at=VALUES(created_at), updated_at=VALUES(updated_at), deleted=VALUES(deleted)";
    $conn->query($sql4);

    // Generate random level and corresponding experience
    $randomLevel = rand(1, 8);
    $experience = rand($levels[$randomLevel], $levels[$randomLevel + 1] ?? $levels[8]);

    // Random profile background
    $profilebg = $profile_bgs[rand(0, count($profile_bgs) - 1)];

    // Trusted status
    $trusted = rand(0, 1);

    $sql5 = "INSERT INTO VENDORS (id, vendor_level, experience, about, profilebg, trusted, created_at, updated_at)
        VALUES ('$vendorId', '$randomLevel', '$experience', '', '$profilebg', '$trusted', NOW(), NOW())
        ON DUPLICATE KEY UPDATE vendor_level=VALUES(vendor_level), experience=VALUES(experience), about=VALUES(about), profilebg=VALUES(profilebg), trusted=VALUES(trusted), created_at=VALUES(created_at), updated_at=VALUES(updated_at)";
    $conn->query($sql5);
}
?>