{
split($0,a,":")
grab=substr($1,2,15)
if (grab == "approx_interval" ) {
printf("        %sapprox_interval%s: %s%s%s,\n","\"","\"","\"",number,"\"")
} else {
print $0
}
}
