set +x

ENDPOINT=https://bfm2tp91fe.execute-api.eu-north-1.amazonaws.com/dev

echo 'get root'
curl -w "\nRESULT: %{http_code}\n" $ENDPOINT
echo
echo 'get app list'
curl -w "\nRESULT: %{http_code}\n" $ENDPOINT/app
echo
echo 'get app item'
curl -w "\nRESULT: %{http_code}\n" $ENDPOINT/app/123
echo
echo 'get app cluster list'
curl -w "\nRESULT: %{http_code}\n" $ENDPOINT/app/123/cluster
echo
echo 'get app cluster item'
curl -w "\nRESULT: %{http_code}\n" $ENDPOINT/app/123/cluster/456
echo
echo 'get cluster list'
curl -w "\nRESULT: %{http_code}\n" $ENDPOINT/cluster
echo
echo 'get cluster item'
curl -w "\nRESULT: %{http_code}\n" $ENDPOINT/cluster/123
echo
echo 'get cluster app list'
curl -w "\nRESULT: %{http_code}\n" $ENDPOINT/cluster/123/app
echo
echo 'get cluster app item'
curl -w "\nRESULT: %{http_code}\n" $ENDPOINT/cluster/123/app/456
echo
echo "--- associations ---"
echo 'put app item 123'
curl -w "\nRESULT: %{http_code}\n" -X PUT $ENDPOINT/app/123
echo
echo 'put cluster item 456'
curl -w "\nRESULT: %{http_code}\n" -X PUT $ENDPOINT/cluster/456
echo
echo 'put cluster item 956'
curl -w "\nRESULT: %{http_code}\n" -X PUT $ENDPOINT/cluster/956
echo
echo 'get app list'
curl -w "\nRESULT: %{http_code}\n" $ENDPOINT/app
echo
echo 'get cluster list'
curl -w "\nRESULT: %{http_code}\n" $ENDPOINT/cluster
echo
echo 'put cluster 456 to app 123'
curl -w "\nRESULT: %{http_code}\n" -X PUT $ENDPOINT/app/123/cluster/456
echo
echo 'put cluster 956 to app 123'
curl -w "\nRESULT: %{http_code}\n" -X PUT $ENDPOINT/app/123/cluster/956
echo
echo 'get app 123 cluster list'
curl -w "\nRESULT: %{http_code}\n" $ENDPOINT/app/123/cluster
echo
echo 'get cluster 456 app list'
curl -w "\nRESULT: %{http_code}\n" $ENDPOINT/cluster/456/app
echo
echo 'get cluster 956 app list'
curl -w "\nRESULT: %{http_code}\n" $ENDPOINT/cluster/956/app
echo