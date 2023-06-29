#execute from the project root

for FNAME in  app logs scripts .gitignore main.py Procfile README.md requirements.txt web.py runtime.txt
do
  rm -rf ../socialmanagerbot/$FNAME
	cp -r $FNAME ../socialmanagerbot/.
done
cd ../socialmanagerbot || exit
git add .
git commit -m"$1"
git push heroku master
echo $(git status)
